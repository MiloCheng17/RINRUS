"""
This is a program written by Qianyi Cheng
at university of memphis.
RINRUS trimming scheme version 2 
Read in rin information for trimming pdb mainchain/sidechain seperatable
Date 7.20.2022
"""
import os, sys, re
from read_write_pdb import *
from copy import *
from check_residue_atom import *
import argparse

######################################   Example   #############################################################
### python3 rinrus_trim2_pdb.py -pdb 3bwm_h_mg.ent -s "A:300,A:301,A:302" -c contact_counts.dat -model 7
### if there is no argument -model, models will generated by adding one residue at a time to the seed 

def gen_res_seq(freqf,sel_key):
    Alist = [chr(i) for i in range(ord('A'),ord('Z')+1)]
    with open(freqf) as f:
        lines = f.readlines()
    sm = len(lines)
    j = len(sel_key)
    qf = {}
    qf[j] = {}
    for i in range(sm):
    #    print(lines[i].split())
        c = lines[i].split()
        if c[0] in Alist:
            cha = c[0]
            res = int(c[1])
            freq = int(c[2])
            if (cha,res) in sel_key: continue
            j += 1
            qf[j] = deepcopy(qf[j-1])
            try:
                qf[j][cha].append(res)
            except:
                qf[j][cha] = [res]
        else:
            cha = ' '
            res = int(c[0])
            freq = int(c[1])
            if (cha,res) in sel_key: continue
            j += 1
            qf[j] = deepcopy(qf[j-1])
            try:
                qf[j][cha].append(res)
            except:
                qf[j][cha] = [res]
    return qf

def trim_pdb_models(sm,res_atom,res_info,pdb_res_name,pdb_res_atom,res_part_list,cha_res_list,Alist,ufree_atoms):
    test = {}
    tot = {}
    res_part_list = {}
    for i in range(sm):
        c = iratoms[i].split()
        res_part_list[(c[0],int(c[1]))]=[]
    for i in range(sm):
        c = iratoms[i].split()
        res_part_list[(c[0],int(c[1]))].append(c[3:])
    for i in res_part_list.keys():
        if len(res_part_list[i]) == 2:
            new_list = res_part_list[i][0] + res_part_list[i][1]
            res_part_list[(i)]=new_list
            
        
        else: 
            new_list = res_part_list[i][0] 
            res_part_list[(i)]=new_list
    
    
    ### check residue atoms itself according to pdb file ###
    for key in sorted(res_part_list.keys()):
        #for res_id in sorted(res_part_list[cha].keys()):
        #    key = (cha,res_id)
        if key in sel_key or pdb_res_name[key] in ('HOH', 'WAT','O') or pdb_res_name[key][:2]=='WT':
            res_part_list[key] = pdb_res_atom[key]
            #res_atom[key] = deepcopy(res_part_list[cha][res_id])
            res_atom[key] = deepcopy(res_part_list[key])
            res_info[key] = []
        else:
            #value_list = deepcopy(res_part_list[cha][res_id])
            value_list = deepcopy(res_part_list[key])
            res_atom[key] = check_sc(pdb_res_name[key],value_list,cres_atoms_sc)

            if not bool(set(res_atom[key])&set(['N','CA','C','O','H','HA','HA2','HA3'])) and 'CB' in res_atom[key]:
                res_info[key] = ['CA']
                res_atom[key].append('CA')
            else:
                res_atom[key] = check_mc(pdb_res_name[key],res_atom[key])

    ### add necessary atoms from adjacent residues to complete peptide bonds ###
    for key in sorted(res_part_list.keys()):
        key = (key[0],key[1])
        cha = key[0]
        res_id = key[1]
        if key not in sel_key and pdb_res_name[key] not in ('HOH', 'WAT','O'):
        ### Check one residue before according to "N and H" ###
            if bool(set(res_atom[key])&set(['N','H'])) and (cha,res_id-1) in pdb_res_name.keys():
                if (cha,res_id-1) not in res_atom.keys():
                    res_atom[(cha,res_id-1)] = ['CA','C','O','HA','HA2','HA3']
                else:
                    for atom in ['CA','C','O','HA','HA2','HA3']:
                        if atom not in res_atom[(cha,res_id-1)]:
                            res_atom[(cha,res_id-1)].append(atom)
        ### Check one residue after according to "C and O" ###
            if bool(set(res_atom[key])&set(['C','O'])) and (cha, res_id+1) in pdb_res_name.keys():
                if (cha,res_id+1) not in res_atom.keys():
                    ### DAW: Check if next residue is proline ###
                    if pdb_res_name[(cha,res_id+1)] == 'PRO':
                        res_atom[(cha,res_id+1)] = ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'HA', '2HB', '3HB', '2HG', '3HG', '2HD', '3HD']
                        ### DAW: Complete the other peptide bond of proline as well ###
                        if (cha,res_id+2) not in res_atom.keys():
                            res_atom[(cha,res_id+2)] = ['CA','HA','HA2','HA3','N','H']
                        else:
                            for atom in ['CA','HA','HA2','HA3','N','H']:
                                if atom not in res_atom[(cha,res_id+2)]:
                                    res_atom[(cha,res_id+2)].append(atom)
                    else:
                        res_atom[(cha,res_id+1)] = ['CA','HA','HA2','HA3','N','H']
                else:
                    for atom in ['CA','HA','HA2','HA3','N','H']:
                        if atom not in res_atom[(cha,res_id+1)]:
                            res_atom[(cha,res_id+1)].append(atom)

    ### Check one "CACA" ###    
    for key in sorted(res_atom.keys()):
        if pdb_res_name[key] not in ('HOH', 'WAT','O') and pdb_res_name[key] in res_atoms_all.keys():
            cha = key[0]
            res_id = key[1]
            if 'CA' in res_atom[key]:
                for atom in ['HA','HA2','HA3']:
                    if atom not in res_atom[key]:
                        res_atom[key].append(atom)
                if (cha,res_id+1) in res_atom.keys() and 'CA' in res_atom[(cha,res_id+1)]:
                    for atom in ['C','O']:
                        if atom not in res_atom[key]:
                            res_atom[key].append(atom)
                    for atom in ['N','H']:
                        if atom not in res_atom[(cha,res_id+1)]:
                            res_atom[(cha,res_id+1)].append(atom)

    ### DAW: if res_atoms still only has CA and/or HA(s), add both sides of MC to avoid methane. Do same for Ala SC to avoid ethane ###
    for key in sorted(res_atom.keys()):
        if key not in sel_key and pdb_res_name[key] not in ('HOH', 'WAT','O'):
            cha = key[0]
            res_id = key[1]
            if (cha,res_id-1) not in res_atom.keys() and (cha,res_id+1) not in res_atom.keys():
                if set(res_atom[key]).issubset({'CA', 'HA', 'HA2', 'HA3'}) or (pdb_res_name[key] in ['ALA'] and set(res_atom[key]).issubset({'CA', 'HA', 'HA2', 'HA3','CB','HB1','HB2','HB3'})):
                    res_atom[key].append('N')
                    res_atom[key].append('H')
                    res_atom[key].append('O')
                    res_atom[key].append('C')
                    res_atom[(cha,res_id-1)] = ['CA','C','O','HA','HA2','HA3']
                    res_atom[(cha,res_id+1)] = ['CA','HA','HA2','HA3','N','H']

    ### Check frozen info ###
    for key in sorted(res_atom.keys()):
        if key not in res_info.keys() and key not in sel_key:
            res_info[key] = ['CA']
        elif key in sel_key and pdb_res_name[key] in res_atoms_all.keys():
            if 'CA' not in res_info[key]:
                try:
                    res_info[key].append('CA')
                except:
                    res_info[key] =['CA']
            if pdb_res_name[key] in ['ARG','LYS','GLU','GLN','MET','TRP','TYR','PHE']:
                res_info[key].append('CB')
            if key in ufree_atoms.keys():
                if 'CA' in ufree_atoms[key]:
                    res_info[key].remove('CA')
                if 'CB' in ufree_atoms[key]:
                    res_info[key].remove('CB')

    res_pick,res_info = final_pick2(pdb,res_atom,res_info,sel_key)

    f1 = open('res_%s_atom_info.dat'%str(sm),'w')        
    f2 = open('res_%s_froz_info.dat'%str(sm),'w')        
    for key in sorted(res_atom.keys()):
        f1.write('%2s %5d '%(key[0],key[1]))
        f2.write('%2s %5d '%(key[0],key[1]))
        for atom in res_atom[key]:
            f1.write('%4s '%atom)
        f1.write('\n')
        for freeze in res_info[key]:
            f2.write('%4s '%freeze)
        f2.write('\n')
    f1.close()
    f2.close()

    outf = 'res_%s.pdb'%str(sm)
    write_pdb(outf,res_pick)

def get_ufree_atom(ufree):
    ufree_atoms = {}
    atoms = ufree.split(',')
    for atom in atoms:
        chain, resid, cacb = atom.split(':')
#        print(chain,resid,cacb)
        key = (chain,int(resid))
        if len(cacb) == 4:
            ufree_atoms[key] = ['CA','CB']
        elif cacb.lower() == 'ca':
            ufree_atoms[key] = ['CA']
        elif cacb.lower() == 'cb':
            ufree_atoms[key] = 'CB'
    return ufree_atoms


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Trim large PDB file according to res_atoms.dat, write trimmed pdb in working directory')
    parser.add_argument('-pdb', dest='r_pdb', default='None', help='protonated pdbfile')
    parser.add_argument('-s', dest='seed', default='None', help='Chain:Resid,Chain:Resid')
    parser.add_argument('-c', dest='r_atom', default='res_atoms.dat', help='atom info for each residue')
    parser.add_argument('-cres', dest='cres', default='None', help='Noncanonical residue information')
    parser.add_argument('-unfrozen', dest='ufree', default='None', help='Seed canonical residue unfrozen CA/CB, chain:Resid:CACB,chain:Resid:CA')
    parser.add_argument('-model', dest='method', default='All', help='generate one or all trimmed models, if "7" is given, then will generate the 7th model')

    args = parser.parse_args()

    r_pdb = args.r_pdb
    seed  = args.seed
    atomf = args.r_atom
    cres  = args.cres
    ufree = args.ufree
    method = args.method
    if cres != 'None':
        cres_atoms_all, cres_atoms_sc = get_noncanonical_resinfo(cres)
    else:
        cres_atoms_all = {}
        cres_atoms_sc = {}

    if ufree != 'None':
        ufree_atoms = get_ufree_atom(ufree)
    else:
        ufree_atoms = {}

    pdb, tres_info, ttot_charge = read_pdb(r_pdb)

    sel_key = get_sel_keys(seed)
    with open(atomf) as f:
        iratoms = f.readlines()
    ### Find sequential of residues in the model ###
    #res_seq = gen_res_seq(atomf,sel_key)

    res_atom = {}   # Residue atoms
    res_info = {}   # Freeze idx for residues

    pdb_res_name = {}
    pdb_res_atom = {}
    for line in pdb:
        key = (line[5],line[6])
        if key not in pdb_res_name.keys():
            pdb_res_name[key] = line[4].strip()
            pdb_res_atom[key] = [line[2].strip()]
        else:
            # print(key,line[2])
            pdb_res_atom[key].append(line[2].strip())

    ### get res_atom info ###
    res_part_list = {}
    cha_res_list = {}
    Alist = [chr(i) for i in range(ord('A'),ord('Z')+1)]
    l_res = len(iratoms)
    
    
    if method == 'All':
        for i in range(len(sel_key),l_res):
            trim_pdb_models(i+1,res_atom,res_info,pdb_res_name,pdb_res_atom,res_part_list,cha_res_list,Alist,ufree_atoms)
    else:
        res_l = int(method)
        trim_pdb_models(res_l,res_atom,res_info,pdb_res_name,pdb_res_atom,res_part_list,cha_res_list,Alist,ufree_atoms)

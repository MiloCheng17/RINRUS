#!/usr/bin/env python3
import os, sys, re
from numpy import *
from read_write_pdb import *
from copy import *
import argparse
import operator
import pandas as pd
import numpy as np


Atoms = {'H' : [1,  1.00794],
         'HE': [2,  4.002602],
         'LI': [3,  6.941],
         'BE': [4,  9.012182],
         'B' : [5,  10.811],
         'C' : [6,  12.0107],
         'N' : [7,  14.00674],
         'O' : [8,  15.9994], 
         'F' : [9,  18.9984],
         'NE': [10, 20.1797],
         'NA': [11, 22.9897],
         'MG': [12, 24.305],
         'AL': [13, 26.9815],
         'SI': [14, 28.0855],
         'P' : [15, 30.9738],
         'S':  [16, 32.065],
         'CL': [17, 35.453],
         'Ar': [18, 39.962383], 
         'K' : [19, 39.0983],
         'CA': [20, 40.078],
         'SC': [21, 44.955912],
         'TI': [22, 47.867000],
         'V' : [23, 50.9415],
         'CR': [24, 51.9961],
         'MN': [25, 54.938],
         'FE': [26, 55.845],
         'NI': [27, 58.6934],
         'CO': [28, 58.9332],
         'CU': [29, 62.939598],
         'ZN': [30, 65.39],
         'GA': [31, 69.723],
         'GE': [32, 72.64],
         'AS': [33, 74.9216],
         'SE': [34, 78.96],
         'BR': [35, 79.904],
         'KR': [36, 83.8],
         'RB': [37, 85.4678],
         'SR': [38, 87.62],
         'Y' : [39, 88.9059],
         'ZR': [40, 91.224],
         'NB': [41, 92.9064],
         'MO': [42, 95.94],
         'TC': [43, 98],
         'RU': [44, 101.07],
         'RH': [45, 102.9055],
         'PD': [46, 106.42],
         'AG': [47, 107.8682],
         'CD': [48, 112.411],
         'IN': [49, 114.818],
         'SN': [50, 118.71],
         'Sb': [51, 121.76],        #Antimony            Sb  51
         'I' : [53, 126.9045],      #Iodine          I   53
         'Te': [52, 127.6],         #Tellurium           Te  52
         'Xe': [54, 131.293],       #Xenon               Xe  54
         'Cs': [55, 132.9055],      #Cesium          Cs  55
         'Ba': [56, 137.327],       #Barium              Ba  56
         'La': [57, 138.9055],      #Lanthanum       La  57
         'Ce': [58, 140.116],       #Cerium              Ce  58
         'Pr': [59, 140.9077],      #Praseodymium    Pr  59
         'Nd': [60, 144.24],        #Neodymium           Nd  60
         'Pm': [61, 145],           #Promethium              Pm  61
         'Sm': [62, 150.36],        #Samarium            Sm  62
         'Eu': [63, 151.964],       #Europium            Eu  63
         'Gd': [64, 157.25],        #Gadolinium          Gd  64
         'Tb': [65, 158.9253],      #Terbium         Tb  65
         'Dy': [66, 162.5],         #Dysprosium          Dy  66
         'Ho': [67, 164.9303],      #Holmium         Ho  67
         'Er': [68, 167.259],       #Erbium              Er  68
         'Tm': [69, 168.9342],      #Thulium         Tm  69
         'Yb': [70, 173.04],        #Ytterbium           Yb  70
         'Lu': [71, 174.967],       #Lutetium            Lu  71
         'Hf': [72, 178.49],        #Hafnium             Hf  72
         'Ta': [73, 180.9479],      #Tantalum        Ta  73
         'W' : [74, 183.84],        #Tungsten            W   74
         'Re': [75, 186.207],       #Rhenium             Re  75
         'Os': [76, 190.23],        #Osmium              Os  76
         'Ir': [77, 192.217],       #Iridium             Ir  77
         'Pt': [78, 195.078],       #Platinum            Pt  78
         'Au': [79, 196.9665],      #Gold            Au  79
         'Hg': [80, 200.59],        #Mercury             Hg  80
         'Tl': [81, 204.3833],      #Thallium        Tl  81
         'Pb': [82, 207.2],         #Lead                Pb  82
         'Bi': [83, 208.9804],      #Bismuth         Bi  83
         'Po': [84, 209],           #Polonium                Po  84
         'At': [85, 210],           #Astatine                At  85
         'Rn': [86, 222],           #Radon                   Rn  86
         'Fr': [87, 223],           #Francium                Fr  87
         'Ra': [88, 226],           #Radium                  Ra  88
         'Ac': [89, 227],           #Actinium                Ac  89
         'Pa': [91, 231.0359],      # Protactinium    Pa  91
         'Th': [90, 232.0381],      # Thorium         Th  90
         'Np': [93, 237],           # Neptunium               Np  93
         'U' : [92, 238.0289],      # Uranium         U   92
         'Am': [95, 243],           # Americium               Am  95
         'Pu': [94, 244],           # Plutonium               Pu  94
         'Cm': [96, 247],           # Curium                  Cm  96
         'Bk': [97, 247],           # Berkelium               Bk  97
         'Cf': [98, 251],           # Californium             Cf  98
         'Es': [99, 252],           # Einsteinium             Es  99
         'Fm': [100,    257],       #Fermium                 Fm  100 
         'Md': [101,    258],       #Mendelevium             Md  101 
         'No': [102,    259],       #Nobelium                No  102 
         'Rf': [104,    261],       #Rutherfordium           Rf  104 
         'Lr': [103,    262],       #Lawrencium              Lr  103 
         'Db': [105,    262],       #Dubnium                 Db  105 
         'Bh': [107,    264],       #Bohrium                 Bh  107 
         'Sg': [106,    266],       #Seaborgium              Sg  106 
         'Mt': [109,    268],       #Meitnerium              Mt  109 
         'Rg': [111,    272],       #Roentgenium             Rg  111 
         'Hs': [108,    277],       #Hassium                 Hs  108 
         'Ds': [110,    0],         #Darmstadtium                Ds  110 
         'Cn': [112,    0],         #Copernicium                 Cn  112 
         'Nh': [113,    0],         #Nihonium                    Nh  113 
         'Fl': [114,    0],         #Flerovium                   Fl  114 
         'Mc': [115,    0],         #Moscovium                   Mc  115 
         'Lv': [116,    0],         #Livermorium                 Lv  116 
         'Ts': [117,    0],         #Tennessine                  Ts  117 
         'Og': [118,    0]          #Oganesson                   Og  118 
         }


def center_of_mass(mass,coord):
    mass = mass.astype(float)[:,newaxis]
    coord = coord.astype(float)
    return sum(coord*mass,axis=0)/sum(mass)


def avg_coord(coord):      ## average coordiante of a residue
    return mean(coord,axis=0)


def calc_dist(a,b):  ## a and b a xyz coordinates array
    return sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 )


def get_model_res(idx_list,freqf,res_id):
    qf = {}
    j = len(idx_list)
    qf[j] = {}
    for i in idx_list:
        try:
            qf[j][i[0]].append(i[1])
        except:
            qf[j][i[0]] = [i[1]]
    with open(freqf) as f:
        lines = f.readlines()
    sm = len(lines)
    for i in range(j,sm):
        c = lines[i].split()
        Alist = [chr(i) for i in range(ord('A'),ord('Z')+1)]
        if c[0] in Alist:
            cha = c[0]
            res = int(c[1])
            dist = float(c[2])
            if (cha,res) in idx_list: continue
            j += 1
            qf[j] = deepcopy(qf[j-1])
            try:
                qf[j][cha].append(res)
            except:
                qf[j][cha] = [res]
        else:
            cha = ' '
            res = int(c[0])
            dist = float(c[1])
            if (cha,res) in idx_list: continue
            j += 1
            qf[j] = deepcopy(qf[j-1])
            try:
                qf[j][cha].append(res)
            except:
                qf[j][cha] = [res]
    return qf        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Distance rule based model generator')
    parser.add_argument('-type', dest='typef', default=None, help='"mass" or "avg"')
    parser.add_argument('-nohydro', action='store_true', help='If flag present, ignore hydrogen atoms from distance calculations')
    parser.add_argument('-pdb', dest='pdbf', default=None, help='pdb_to_treat')
    parser.add_argument('-cut', dest='coff', default=3, help='cut_off_dist, default=3')
    parser.add_argument('-s', dest='seed', default=None, help='center_residues, examples: A:300,A:301,A:302')

    args = parser.parse_args()
    res_atom = {}
    res_name = {}
    res_cout = {}
    res_info = {}
    pdb_res_name = {}
    cres_atom = {}


    type=args.typef
    pdbf = args.pdbf
    pdb, res_info, tot_charge = read_pdb(pdbf)

    cut = float(args.coff)
    
    ###### Find center of mass point x,y,z ######
    cres = args.seed
    center_res = cres.split(',')
    idx_list = []
    res_id = {}
    test_dict = {}
    for i in range(len(center_res)):
        a,b = center_res[i].split(':')
        idx_list.append([a,int(b)])
        res_id[(a,int(b))] = [0.00]
    sel_atoms = []
    sel_coord = []
    for i in range(len(center_res)):
        for atom in pdb:
            if args.nohydro==True and atom[14].strip()=="H": 
                continue
            if idx_list[i][0] == atom[5].strip() and idx_list[i][1] == atom[6]:
                sel_atoms.append(Atoms[atom[14].strip()][1])
                sel_coord.append([atom[8],atom[9],atom[10]])
    sel_coord = array(sel_coord)
    sel_atoms = array(sel_atoms)

   ## On July 2022-Tejas Suhagia, added step to generate based on center of mass and average of xyz with and without hydrogen , also changed README for that.

    if args.nohydro==True:
            print("-nohydrogen is selected so hydrogen is neglacted")
    if type=="mass":
        com = center_of_mass(sel_atoms,sel_coord)
        
        print("Center of mass type is selected")
    elif type=="avg":    
        com=avg_coord(sel_coord)
        print("XYZ average type is selected")
   

    ###### Calculate atom-pair distances ######
    dist_atom = []
    dist_atom_dict = {}
    for atom in pdb:
        if args.nohydro==True and atom[14].strip()=="H": 
                continue
        dist_atom.append([calc_dist(array([atom[8],atom[9],atom[10]]),com),atom[5].strip(),atom[6],atom[2].strip()])
   
    for dist_p in dist_atom:
        if dist_p[0] <= cut:
            if (dist_p[1],dist_p[2]) not in res_id.keys():
                res_id[(dist_p[1],dist_p[2])] = [dist_p[0],dist_p[3]]
                test_dict[(dist_p[1],dist_p[2]),dist_p[3]]=[dist_p[0],dist_p[3]]

            else:
                res_id[(dist_p[1],dist_p[2])][0] = min(dist_p[0],res_id[(dist_p[1],dist_p[2])][0])
            
                test_dict[(dist_p[1],dist_p[2]),dist_p[3]]=[dist_p[0],dist_p[3]]
                
                res_id[(dist_p[1],dist_p[2])].append(dist_p[3])
             #   print((a,int(b)))
             #   test_dict[(a,int(b)),dist_p[3]]=[0.00,dist_p[3]]
    #print(res_id)
    res_id = dict(sorted(res_id.items(),key=lambda x:x[1]))
 
 #################################################### TAYLOR ADDITIONS #########################################################
    atom_dict_5 = {}
    for val in res_id:
        atom_dict_5[val]=[]
    for val in res_id:
        for lst in res_id[val][1:]:
            atom_dict_5[val].append(test_dict[val,lst])
    sorter_atom = {}
    main = []
    side = []
    final = {}
    num_5 = 0
    num_6 = 0
    aa = {}
    df_6 = {'ChainID':[],'res_name':[],'res_num':[],'Main atm type':[],'Main Chain':[],'Side atm type':[],'Side Chain':[]}
    for val_2 in res_id:
        aa[val_2]={}
    for key_3 in res_id:
        for let in atom_dict_5[key_3]:
            aa[key_3][let[1]]=let[0]
    for val_3 in res_id:
        df_6['ChainID'].append(val_3[0])
        df_6['res_num'].append(val_3[1])
        main ={}
        side = {}
        for key_3 in aa[val_3]:
            if key_3 == 'N' or key_3 == 'CA' or key_3 == 'O' or key_3 == 'C':
                main[val_3,key_3]=aa[val_3][key_3]
            else:
                side[val_3,key_3]=aa[val_3][key_3]
        if main == {}:
            df_6['Main atm type'].append('')
            df_6['Main Chain'].append('')
            pass
        else:
            first_hit = sorted(main.items(), key=lambda x: x[1])[0]
            matm = first_hit[0][1]
            dist = first_hit[1]
            df_6['Main atm type'].append(matm)
            df_6['Main Chain'].append(dist)
        if side == {}:
            df_6['Side atm type'].append('')
            df_6['Side Chain'].append('')
            pass
        else:
            first_hit = sorted(side.items(), key=lambda x: x[1])[0]
            satm = first_hit[0][1]
            dist = first_hit[1]
            df_6['Side atm type'].append(satm)
            df_6['Side Chain'].append(dist)
    ##########################################################################################################################################

    
    

        
        

    
    


           
   

 
    
    
    
    d_res = open('dist_per_res-%.2f.dat'%cut,'w')
    d_res = open('res_atom-%.2f.dat'%cut,'w')
    for key in res_id.keys():
        d_res.write('%-2s %-5s %-7.4f'%(key[0],key[1],res_id[key][0]))
        for v in range(1,len(res_id[key])):
            d_res.write(' %-6s'%res_id[key][v])
        d_res.write('\n')
    d_res.close()
    


            

   ## On June 2022-Tejas Suhagia, added step to generate res_atoms_xx.dat which is needed for next steps, also changed README for that.
    atom_res = open('res_atom-%.2f.dat'%cut,'w')
    for key in res_id.keys():
        atom_res.write('%-2s %-5s '%(key[0],key[1]))
        for v in range(1,len(res_id[key])):
            atom_res.write(' %-6s'%res_id[key][v])
        atom_res.write('\n')
    atom_res.close()
    
    
    #### On Jan 2023 Taylor additions, creates a csv file and prints out a dataframe of results. The script reads the dist_per_res dat file and creates three lists 
    # with the chain id, residue number and distance. These three lists are turned into a pandas dataframe. The dataframe is then turned into a list. 
    # This list is looped through the pdb file to find that res name based on the chain id and res num. Following, a csv file is printed out that includes the chain id, res name and res num. ####

                    
        #### On Jan 2023 Taylor additions, creates a csv file and prints out a dataframe of results. The script reads the dist_per_res dat file and creates three lists 
    # with the chain id, residue number and distance. These three lists are turned into a pandas dataframe. The dataframe is then turned into a list. 
    # This list is looped through the pdb file to find that res name based on the chain id and res num. Following, a csv file is printed out that includes the chain id, res name and res num. ####
    chain_id = []
    res_num = []
    dist = []
    atm_id = []
    amino_name = {}
    amino_name_lst = []
    with open('dist_per_res-%.2f.dat'%cut,'r') as fp:
        lines = fp.readlines()
        for i in lines:
            a = i.split(' ')
            no_space = []
            for sp in a:
                if sp == '':
                    pass
                else:
                    no_space.append(sp)
            chain_id.append(no_space[0])
            res_num.append(no_space[1])
            dist.append(no_space[2])
            atm_id.append(no_space[3:])

    df = {'chain ID':chain_id,'res num':res_num,'Dist':dist}
    look_up_these = []
    for num,id in enumerate(df['chain ID']):
        look_up_these.append((id,df['res num'][num],df['Dist'][num]))
    aa = {}
    for tup in look_up_these:
        for line in pdb:
            if str(tup[0]) == str(line[5]) and str(tup[1])==str(line[6]):
                    aa[str(line[5])+','+str(line[4])+str(line[6])+','+str(tup[2])]=''
                    amino_name[str(line[5])+','+str(line[4])+str(line[6])+','+str(tup[2])] = ''
    for name in amino_name.keys():
        #print(name)
        name = name.split(',')
        amino_name_lst.append(name[1])
                    
                    
    with open('data_name-%.2f.csv'%cut,'w') as fp:
        fp.write('Chain,' + 'res and ID,'+'distance\n')
    with open('data_name-%.2f.csv'%cut,'a') as fp:
        for i in aa.keys():
            a = i.split(',')
            df_6['res_name'].append(a[1])
            fp.write(str(i)+'\n')
            
                 

    
    df_6 = pd.DataFrame(df_6)
    #print(df_6)
    df_6.to_csv('data_analysis_output_-%.2f.csv'%cut,index=False)
    
    #'Main atm type':[],'Main Chain':[],'Side atm type':[],'Side Chain':[]
    
df_test ={'ChainID':[],'res & ID':[],'comb_atm_type':[],'distance':[]} 
for line in df_6['Main atm type']:
    df_test['comb_atm_type'].append(line)
for line in df_6['Main Chain']:
    if line == '':
        df_test['distance'].append(np.nan)
    else:
        df_test['distance'].append(round(float(line),4))
for line in df_6['Side atm type']:
    df_test['comb_atm_type'].append(line)
for line in df_6['Side Chain']:
    if line == '':
        df_test['distance'].append(np.nan)
    else:
        df_test['distance'].append(round(float(line),4))
for line in df_6['res_name']:
    df_test['res & ID'].append(line)
for line in df_6['res_name']:
    df_test['res & ID'].append(line)
    
for line in df_6['ChainID']:
    df_test['ChainID'].append(line)
for line in df_6['ChainID']:
    df_test['ChainID'].append(line)
    
df_test = pd.DataFrame(df_test)
print(df_6)
df_test = df_test.sort_values(by=['distance'])
print(df_test)
df_test.to_csv('combined_output_-%.2f.csv'%cut,index=False)
    

        
        

    
    


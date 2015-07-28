base1  = 'TTTTTTTTTTTTTTTTCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGG'
base2  = 'TTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGG'
base3  = 'TCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAG'
code_dict={}
#universal
AAs1  =   'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
starts1 = '-----------------------------------M----------------------------'
universal={'AAS':AAs1,'btarts':starts1,'base1':base1,'base2':base2,'base3':base3,'start':"ATG","end":"TAA,TAG,TGA"}
code_dict["universal"]=universal

#The Euplotid Nuclear Code
AAs2 = 'FFLLSSSSYY**CCCWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
starts2 = '-----------------------------------M----------------------------'
Euplotes={'AAS':AAs2,'btarts':starts2,'base1':base1,'base2':base2,'base3':base3,'start':"ATG","end":"TAA,TAG"}
code_dict["Euplotes"]=Euplotes

#The Alternative Yeast Nuclear Code
AAs3 = 'FFLLSSSSYY**CC*WLLLSPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
starts3 = '-------------------M---------------M----------------------------'
Candida={'AAS':AAs3,'btarts':starts3,'base1':base1,'base2':base2,'base3':base3,'start':"ATG,CTG","end":"TAA,TAG,TGA"}
code_dict["Candida"]=Candida

#The Ciliate, Dasycladacean and Hexamita Nuclear Code
AAs4 = 'FFLLSSSSYYQQCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
starts4 = '-----------------------------------M----------------------------'
Tetrahymena={'AAS':AAs4,'btarts':starts4,'base1':base1,'base2':base2,'base3':base3,'start':'ATG',"end":"TGA"}
code_dict["Tetrahymena"]=Tetrahymena

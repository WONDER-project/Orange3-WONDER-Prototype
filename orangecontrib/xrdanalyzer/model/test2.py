from orangecontrib.xrdanalyzer.model.diffractionpattern import DiffractionPoint, DiffractionPatternFactory


#diffclass = DiffractionPoint(2,3.3,0.5)

#print(diffclass.get_array())
#pattern = DiffractionPatternFactory.creat_diffraction_pattern_from_file("/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/CaF2P464h.xye")
pattern = DiffractionPatternFactory.creat_diffraction_pattern_from_file("C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\CaF2P464h.xye")

if True:

    print (pattern.points_count())

    #for index in range(0, list.atoms_count()):
    #    atom = list.get_atom(index)

    #    print(atom.z_element, atom.coordinates.x, atom.coordinates.y, atom.coordinates.z )

    #print(list.matrix()[20][1])


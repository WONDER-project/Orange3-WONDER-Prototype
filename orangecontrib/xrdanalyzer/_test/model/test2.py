from orangecontrib.xrdanalyzer.model.diffractionpattern import DiffractionPoint, DiffractionPatternFactory


#diffclass = DiffractionPoint(2,3.3,0.5)

#print(diffclass.get_array())
#pattern = DiffractionPatternFactory.creat_diffraction_pattern_from_file("/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/CaF2P464h.xye")
pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file("C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\CaF2P464h.raw")


point1 = DiffractionPoint(twotheta=1)

#print(point1.get_array())
if True:


    print (pattern.diffraction_points_count())

    for index in range(0, pattern.diffraction_points_count()):
        point = pattern.get_diffraction_point(index)

        print(point.twotheta, point.intensity)

    #print(list.matrix()[20][1])



from orangecontrib.xrdanalyzer.model.atom import AtomListFactory


list = AtomListFactory.create_atom_list_from_file("/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.np")

print (list.atoms_count())

for index in range(0, list.atoms_count()):
    atom = list.get_atom(index)

    print(atom.z_element, atom.coordinates.x, atom.coordinates.y, atom.coordinates.z )

print(list.matrix()[20][1])
#iterates over the functions matrix
import collapser

def iterate(con,matrix,num_deployable_units):
	matrix = []
	matrix[0] = ['Matrix', 'file_main.main', ['dir1.file1.f1', 'dir1.file1.f2'], 'dir1.file2.f3', 'dir2.file3.f4', 'dir2.file3.f5']
	matrix[1] = ['file_main.main', 0, 0, 0, 0, 0]
	matrix[2] = [['dir1.file1.f1', 'dir1.file1.f2'],1,0,0,0,0]
	matrix[3] = ['dir1.file2.f3',1,0,0,0,0]
	matrix[4] = ['dir2.file3.f4',0,0,0,0,0]
	matrix[5] = ['dir2.file3.f5',0,0,0,0,0]

	return matrix
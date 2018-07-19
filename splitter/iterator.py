#iterates over the functions matrix
import collapser

def iterate_fake(con,matrix,num_deployable_units):
	matrix = []
	matrix[0] = ['Matrix', 'file_main.main', ['dir1.file1.f1', 'dir1.file1.f2'], 'dir1.file2.f3', 'dir2.file3.f4', 'dir2.file3.f5']
	matrix[1] = ['file_main.main', 0, 0, 0, 0, 0]
	matrix[2] = [['dir1.file1.f1', 'dir1.file1.f2'],1,0,0,0,0]
	matrix[3] = ['dir1.file2.f3',1,0,0,0,0]
	matrix[4] = ['dir2.file3.f4',0,0,0,0,0]
	matrix[5] = ['dir2.file3.f5',0,0,0,0,0]

	return matrix


def iterate(con,matrix,desired_num_du)
	''' this function receives the matrix as input and the number of desired DUs.
		The desired number of DUs will be (normally) the number of available machines.
		Therefore the final number of DUs must be equal or bigger than number of desired DUs.
		Without any iteration, the number of DU is the number of functions.
		The matrix will be colapsed iteratively, reducing the number of DUs, by colapsing the 
		pair of functions which invoke each other more times.
		when the number of DU is equal to number of desired DUs, then the process stops'''


		# for testing
		return iterate_fake(con,matrix,desired_num_du)
		#iteration 0
		num_du= len(matrix[0])-1





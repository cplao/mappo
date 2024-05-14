
def read_csv(filename):

    with open(filename, 'r') as f:
        lines = f.readlines()
        matrix = [[int(num) for num in line.split()] for line in lines]
        print(matrix)
        return matrix
    
    return None

read_csv('matrix.txt')

# TODO cache decorator
# 
# def get_hash_calc(num_pieces, size):
#     """return hash calculator. Store table of values."""
#     table = [0]*size
#     table[0] = 1
#     for p in range(1, size):
#         table[p] = table[p-1] * num_pieces
# 
#     def hash_calc(piece, position):
#         """Return hash value to place piece at position on board."""
#         return piece * table[position]
# 
#     return hash_calc 

import cProfile
import pstats
from Simulator import Simulator

cProfile.run("Simulator(5 * 10 * 60, 3000, 5280/4, 5280/4, move=False, uniform=True).run()", filename="profiling/profs/grid_3000.prof")

# p = pstats.Stats("profs/grid_1000.prof")
# p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

# python3 -m snakeviz profiling/profs/grid_1000.prof

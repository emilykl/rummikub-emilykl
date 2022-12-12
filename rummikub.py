from heapq import heappush, heappop, heapify
import itertools

from collections_extended import bag


def main():

    tiles_input = bag(["4B", "5B", "6B", "7B", "8B", "8Y", "8R", "8K", "1B"])

    # 3 red, 3 red, 4 black, 4 red, 5 black, 5 red
    # tiles_input = bag(["3R", "3R", "4K", "4R", "5B", "5R"])

    # 3 red, 3 red, 4 black, 4 red, 5 red, 4 yellow, 4 white, 3 yellow, 3 white
    tiles_input = bag(["3R", "3R", "4B", "4R", "5R", "4Y", "4W", "3Y", "3W"])

    tiles = parse_tiles(tiles_input)

    runs = find_runs(tiles)
    sets = find_sets(tiles)

    tilesets = runs.union(sets)

    # print(f"tiles: {tiles}")
    # print(f"runs: {runs}")
    # print(f"sets: {sets}")

    all_solutions = run_dfs(tiles, tilesets, return_all=True)

    for sol in all_solutions:
        print("\nSolution:")
        print(sol)

    print("\n===\n")

    best_solution = min(all_solutions)
    print(f"Best solution:")
    print(best_solution)
    print(f"Covers {best_solution.size()}/{len(tiles)} tiles")


"""
OK now technically we have enough info to implement graph search to find
a set of sets/runs that covers all tiles (or determine that there is none).

We'll use DFS with priority (i.e. Dijkstra), where the priority of each partial path
is the number of tiles covered. (Sort priority queue in reverse order from usual,
so that paths with highest priority value are on top.)

Nodes = bag of sets/runs applied to current tiles
 ** it is a BAG rather than a SET because the same set/run may be applied
    multiple times if there are enough tiles
Edges = applying an additional set/run to the tiles
Edge weights = number of tiles in applied set/run
"""


def run_dfs(tiles, tilesets, return_all=False):

    # Initialize start node
    # This is a node containing 0 tilesets
    start = Node(bag([]))

    # Initialize visited nodes
    # Initially this is only the starting node
    visited = [start]

    # Initialize to-do list
    # We use a priority queue for this
    # Initially, the to-do list is all nodes reachable from the starting node
    to_do = start.neighbors(tilesets, tiles)
    heapify(to_do)

    while len(to_do) > 0:

        # Pop highest-priority node off the queue
        curr_node = heappop(to_do)

        # Add it to the visited list
        visited.append(curr_node)

        # If it's a valid solution, we are done!
        if curr_node.is_solution(tiles) and not return_all:
            break

        # Otherwise, add current node's neighbors to to-do queue
        for neighbor in curr_node.neighbors(tilesets, tiles):
            heappush(to_do, neighbor)

    # Now, visited list contains all solutions we have tried
    # Get the min node in the list to find the best solution,
    # or return all solutions sorted in order of quality
    if return_all:
        return sorted(visited)
    else:
        return min(visited)


def print_node(node):
    return "Node containing the following tilesets:" + "\n".join(
        ["  " + str(list(ts)) for ts in node.tilesets()]
    )


# Sigh, I didn't really want to make objects for this, but defining a Node
# object and implementing comparison functions allows us to seamlessly use
# the Python `heapq` functions, so... just doing that
# Each Node is essentially just a `bag` with comparisons implemented
class Node:

    # Initialize the node with a bag of tilesets
    def __init__(self, tileset_bag):
        self._tilesets = tileset_bag

    def tilesets(self):
        return self._tilesets

    def __str__(self):
        return "Node containing the following tilesets:\n" + "\n".join(
            ["  " + str(list(ts)) for ts in self._tilesets]
        )

    def size(self):
        return sum([len(ts) for ts in self._tilesets])

    # Return a new node with the same tilesets as the current node,
    # plus the specified tileset
    def _with_tileset(self, tileset):
        new_tilesets = self._tilesets.copy()
        new_tilesets.add(tileset)
        return Node(new_tilesets)

    # Return a bag containing the tiles used in all tilesets
    # of this node.
    def _tiles_used(self):
        return bag([t for _tiles in self._tilesets for t in _tiles])

    # Determine whether node is valid for the given set of tiles
    # A node is valid if all tilesets in the node can be made
    # simultaneously using the given tiles
    def is_valid(self, tiles):
        return self._tiles_used().issubset(tiles)

    # Determine whether this node is a full solution for the given
    # set of tiles. A node is a solution iff the tiles contained in its
    # tilesets are exactly the same tiles passed to this function.
    def is_solution(self, tiles):
        return self._tiles_used() == tiles

    # Based on the given tiles and valid tilesets,
    # return the list of nodes reachable from this node.
    # A node is reachable iff:
    #  - It contains exactly one additional valid tileset
    #     compared to the given node
    #  - It is a valid node (see is_valid() above)
    def neighbors(self, all_tilesets, tiles):
        possible_neighbors = [self._with_tileset(ts) for ts in all_tilesets]
        return [n for n in possible_neighbors if n.is_valid(tiles)]

    # Use @functools.total_ordering to implement comparisons
    # The total ordering is based on the number of tiles in all sets in the bag
    # like so:
    #     value = sum([len(ts) for ts in self._tilesets])

    # I don't have the reference for that handy, so for now I'll just define
    # the comparison functions manually
    # Note that these are intentionally reversed, so that the node with the
    # highest value shows up at the top of the heap
    def __lt__(self, other):
        return self.size() > other.size()

    def __le__(self, other):
        return self.size() >= other.size()

    def __gt__(self, other):
        return self.size() < other.size()

    def __ge__(self, other):
        return self.size() <= other.size()

    def __eq__(self, other):
        return self.size() == other.size()


def parse_tiles(tiles_input):
    return [(int(tile[0]), tile[1]) for tile in tiles_input]


def remove_duplicates(tiles):
    return list(set(tiles))


def group_by_color(tiles):
    colors = set([tile[1] for tile in tiles])
    return {color: [tile for tile in tiles if tile[1] == color] for color in colors}


def find_runs(tiles):
    tiles = remove_duplicates(tiles)
    grouped = group_by_color(tiles)
    runs = []

    for _, color_tiles in grouped.items():
        color_tiles_sorted = sorted(color_tiles)
        runs.extend(sequences(color_tiles_sorted))

    return set(runs)


def find_sets(tiles):
    tiles = remove_duplicates(tiles)
    grouped = group_by_number(tiles)
    sets = []

    for _, number_tiles in grouped.items():
        if len(number_tiles) >= 3:
            sets.extend(frozenset(x) for x in itertools.combinations(number_tiles, 3))
            sets.extend(frozenset(x) for x in itertools.combinations(number_tiles, 4))

    return set(sets)


def group_by_number(tiles):
    numbers = set([tile[0] for tile in tiles])
    return {n: [tile for tile in tiles if tile[0] == n] for n in numbers}


def sequences(tiles):
    # Find increasing sequences of min length 3
    # in a list of already-sorted tiles
    sequences = []
    for i in range(len(tiles)):
        for j in range(i + 3, len(tiles)):
            if [tile[0] for tile in tiles[i:j]] == list(
                range(tiles[i][0], tiles[j][0])
            ):
                sequences.append(frozenset(tiles[i:j]))
    return frozenset(sequences)


if __name__ == "__main__":
    main()

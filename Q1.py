import http.client
import json
import csv
import requests


#############################################################################################################################
# cse6242 
# All instructions, code comments, etc. contained within this notebook are part of the assignment instructions.
# Portions of this file will auto-graded in Gradescope using different sets of parameters / data to ensure that values are not
# hard-coded.
#
# Instructions:  Implement all methods in this file that have a return
# value of 'NotImplemented'. See the documentation within each method for specific details, including
# the expected return value
#
# Helper Functions:
# You are permitted to write additional helper functions/methods or use additional instance variables within
# the `Graph` class or `TMDbAPIUtils` class so long as the originally included methods work as required.
#
# Use:
# The `Graph` class  is used to represent and store the data for the TMDb co-actor network graph.  This class must
# also provide some basic analytics, i.e., number of nodes, edges, and nodes with the highest degree.
#
# The `TMDbAPIUtils` class is used to retrieve Actor/Movie data using themoviedb.org API.  We have provided a few necessary methods
# to test your code w/ the API, e.g.: get_movie_cast(), get_movie_credits_for_person().  You may add additional
# methods and instance variables as desired (see Helper Functions).
#
# The data that you retrieve from the TMDb API is used to build your graph using the Graph class.  After you build your graph using the
# TMDb API data, use the Graph class write_edges_file & write_nodes_file methods to produce the separate nodes and edges
# .csv files for submission to Gradescope.
#
# While building the co-actor graph, you will be required to write code to expand the graph by iterating
# through a portion of the graph nodes and finding similar artists using the TMDb API. We will not grade this code directly
# but will grade the resulting graph data in your nodes and edges .csv files.
#
#############################################################################################################################


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str) -> None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """
        node = (id, name)
        if node not in self.nodes:
            self.nodes.append(node)


    def add_edge(self, source: str, target: str) -> None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """
        edge = (source, target)
        reverse_edge = (target, source)
        # For undirected graph, check if edge exists in either direction
        if edge not in self.edges and reverse_edge not in self.edges:
            self.edges.append(edge)


    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)


    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)


    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        # Count the degree for each node
        degree_count = {}
        
        for node_id, _ in self.nodes:
            degree_count[node_id] = 0
        
        # For undirected graph, count each edge for both nodes
        for source, target in self.edges:
            if source in degree_count:
                degree_count[source] += 1
            if target in degree_count:
                degree_count[target] += 1
        
        # Find the maximum degree
        if not degree_count:
            return {}
        
        max_degree = max(degree_count.values())
        
        # Return all nodes with the maximum degree
        return {node_id: degree for node_id, degree in degree_count.items() if degree == max_degree}


    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list[int]=None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param string movie_id: a movie_id
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :param integer limit: maximum number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range). 
            If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
            If after excluding, the limit is not specified, then return all remaining cast members."
            e.g., if limit=5 and the actor whose id corresponds to cast member with order=1 is to be excluded,
            return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': '97909' # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
                Note that this is an example of the structure of the list and some of the fields returned by the API.
                The result of the API call will include many more fields for each cast member.
        """
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            cast = data.get('cast', [])
            
            # Filter by limit first (order 0 to limit-1)
            if limit is not None:
                cast = [member for member in cast if member.get('order', float('inf')) < limit]
            
            # Then exclude specified ids
            if exclude_ids is not None:
                cast = [member for member in cast if member.get('id') not in exclude_ids]
            
            return cast
            
        except Exception as e:
            print(f"Error fetching movie cast for movie_id {movie_id}: {e}")
            return []


    def get_movie_credits_for_person(self, person_id: str, start_date: str = None, end_date: str = None) -> list:
        """
        Using the TMDb API, get the movie credits for a person serving in a cast role
        documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits

        :param string person_id: the id of a person
        :param start_date: optional parameter to return the movie credit if the release date >= the specified date
            dates should be formatted like 'YYYY-MM-DD'
            e.g., if the start_date is '2024-01-01', then only return credits with a release_date on or after '2024-01-01'
        :param end_date: optional parameter to return the movie credit if the release date <= the specified date
            dates should be formatted like 'YYYY-MM-DD'
            e.g., if the end_date is '2024-01-01', then only return credits with a release_date on or before '2024-01-01'
        :rtype: list
            return a list of dicts, one dict per movie credit with the following structure:
                [{'id': '97909' # the id of the movie credit
                'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                'release_date': '2024-01-01' # the string value of the release_date value for the credit}, ... ]
        
        IMPORTANT: You should format your dates like 'YYYY-MM-DD' e.g. '2024-01-29'.  You can assume the API will 
            format them in the same way. You can compare these as strings without doing any conversion.
        """
        url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            cast_credits = data.get('cast', [])
            
            # Filter by date range
            filtered_credits = []
            for credit in cast_credits:
                release_date = credit.get('release_date', '')
                
                # Skip if no release date
                if not release_date:
                    continue
                
                # Check start_date
                if start_date and release_date < start_date:
                    continue
                
                # Check end_date
                if end_date and release_date > end_date:
                    continue
                
                # Add to filtered list with required fields
                filtered_credits.append({
                    'id': credit.get('id'),
                    'title': credit.get('title'),
                    'release_date': release_date
                })
            
            return filtered_credits
            
        except Exception as e:
            print(f"Error fetching movie credits for person_id {person_id}: {e}")
            return []


#############################################################################################################################
#
# BUILDING YOUR GRAPH
#
# Working with the API:  See use of http.request: https://docs.python.org/3/library/http.client.html#examples
#
# Using TMDb's API, build a co-actor network for the actor's/actress' movies released in 1999.
# In this graph, each node represents an actor
# An edge between any two nodes indicates that the two actors/actresses acted in a movie together in 1999.
# i.e., they share a movie credit.
# e.g., An edge between Samuel L. Jackson and Robert Downey Jr. indicates that they have acted in one
# or more movies together in 1999.
#
# For this assignment, we are interested in a co-actor network of movies in 1999; specifically,
# we only want the first 5 co-actors in each movie credit with a release date in 1999.
# Build your co-actor graph on the actor 'Laurence Fishburne' w/ person_id 2975.
#
# You will need to add extra functions or code to accomplish this.  We will not directly call or explicitly grade your
# algorithm. We will instead measure the correctness of your output by evaluating the data in your nodes.csv and edges.csv files.
#
# GRAPH SIZE
# Since the TMDB API is a live database, the number of nodes / edges in the final graph will vary slightly depending on when
# you execute your graph building code. We take this into account by rebuilding the solution graph every few days and
# updating the auto-grader.  We compare your graph to our solution with a margin of +/- 200 for nodes and +/- 300 for edges.
# 
# e.g., if the current solution contains 507 nodes then the min/max range is 307-707.
# The same method is used to calculate the edges with the exception of using the aforementioned edge margin.
# ----------------------------------------------------------------------------------------------------------------------
# BEGIN BUILD CO-ACTOR NETWORK
#
# INITIALIZE GRAPH
#   Initialize a Graph object with a single node representing Laurence Fishburne
#
# BEGIN BUILD BASE GRAPH:
#   Find all of Laurence Fishburne's movie credits that have a release date in 1999.
#   FOR each movie credit:
#   |   get the movie cast members having an 'order' value between 0-4 (these are the co-actors)
#   |
#   |   FOR each movie cast member:
#   |   |   using graph.add_node(), add the movie cast member as a node (keep track of all new nodes added to the graph)
#   |   |   using graph.add_edge(), add an edge between the Laurence Fishburne (actor) node
#   |   |   and each new node (co-actor/co-actress)
#   |   END FOR
#   END FOR
# END BUILD BASE GRAPH
#
#
# BEGIN LOOP - DO 2 TIMES:
#   IF first iteration of loop:
#   |   nodes = The nodes added in the BUILD BASE GRAPH (this excludes the original node of Laurence Fishburne!)
#   ELSE
#   |    nodes = The nodes added in the previous iteration:
#   ENDIF
#
#   FOR each node in nodes:
#   |  get the movie credits for the actor that have a release date in 1999.
#   |
#   |   FOR each movie credit:
#   |   |   try to get the 5 movie cast members having an 'order' value between 0-4
#   |   |
#   |   |   FOR each movie cast member:
#   |   |   |   IF the node doesn't already exist:
#   |   |   |   |    add the node to the graph (track all new nodes added to the graph)
#   |   |   |   ENDIF
#   |   |   |
#   |   |   |   IF the edge does not exist:
#   |   |   |   |   add an edge between the node (actor) and the new node (co-actor/co-actress)
#   |   |   |   ENDIF
#   |   |   END FOR
#   |   END FOR
#   END FOR
# END LOOP
#
# Your graph should not have any duplicate edges or nodes
# Write out your finished graph as a nodes file and an edges file using:
#   graph.write_edges_file()
#   graph.write_nodes_file()
#
# END BUILD CO-ACTOR NETWORK
# ----------------------------------------------------------------------------------------------------------------------

# Exception handling and best practices
# - You should use the param 'language=en-US' in all API calls to avoid encoding issues when writing data to file.
# - If the actor name has a comma char ',' it should be removed to prevent extra columns from being inserted into the .csv file
# - Some movie_credits do not return cast data. Handle this situation by skipping these instances.
# - While The TMDb API does not have a rate-limiting scheme in place, consider that making hundreds / thousands of calls
#   can occasionally result in timeout errors. If you continue to experience 'ConnectionRefusedError : [Errno 61] Connection refused',
#   - wait a while and then try again.  It may be necessary to insert periodic sleeps when you are building your graph.


def build_co_actor_network(graph: Graph, tmdb_api_utils: TMDBAPIUtils, start_actor_id: str) -> None:
    """
    Build a co-actor network for movies released in 1999 starting from a given actor.
    
    :param graph: Graph object to populate
    :param tmdb_api_utils: TMDBAPIUtils instance for API calls
    :param start_actor_id: The actor ID to start building the network from
    """
    import time
    
    # Track nodes added in each iteration
    nodes_to_process = []
    
    # BUILD BASE GRAPH
    # Get Laurence Fishburne's 1999 movie credits
    movies_1999 = tmdb_api_utils.get_movie_credits_for_person(
        person_id=start_actor_id,
        start_date='1999-01-01',
        end_date='1999-12-31'
    )
    
    print(f"Found {len(movies_1999)} movies for actor {start_actor_id} in 1999")
    
    # For each movie, get the top 5 cast members (order 0-4)
    for movie in movies_1999:
        movie_id = str(movie['id'])
        
        # Get cast members with order 0-4, excluding the start actor
        cast_members = tmdb_api_utils.get_movie_cast(
            movie_id=movie_id,
            limit=5,
            exclude_ids=[int(start_actor_id)]
        )
        
        # Add each cast member as a node and create edge
        for cast_member in cast_members:
            actor_id = str(cast_member['id'])
            actor_name = cast_member.get('name', '').replace(',', '')  # Remove commas
            
            # Add node (will not duplicate if already exists)
            graph.add_node(id=actor_id, name=actor_name)
            
            # Add edge between start actor and this co-actor
            graph.add_edge(source=start_actor_id, target=actor_id)
            
            # Track this node for next iteration
            if (actor_id, actor_name) not in nodes_to_process:
                nodes_to_process.append((actor_id, actor_name))
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    print(f"Base graph built. Added {len(nodes_to_process)} nodes")
    
    # BEGIN LOOP - DO 2 TIMES
    for iteration in range(2):
        print(f"\nIteration {iteration + 1}/2")
        current_nodes = nodes_to_process.copy()
        nodes_to_process = []  # Reset for next iteration
        
        # For each node from previous iteration
        for node_id, node_name in current_nodes:
            # Get this actor's 1999 movie credits
            actor_movies_1999 = tmdb_api_utils.get_movie_credits_for_person(
                person_id=node_id,
                start_date='1999-01-01',
                end_date='1999-12-31'
            )
            
            # For each movie, get top 5 cast members
            for movie in actor_movies_1999:
                movie_id = str(movie['id'])
                
                # Get cast members with order 0-4, excluding current actor
                cast_members = tmdb_api_utils.get_movie_cast(
                    movie_id=movie_id,
                    limit=5,
                    exclude_ids=[int(node_id)]
                )
                
                # Add each cast member
                for cast_member in cast_members:
                    coactor_id = str(cast_member['id'])
                    coactor_name = cast_member.get('name', '').replace(',', '')
                    
                    # Check if node already exists
                    node_exists = any(n[0] == coactor_id for n in graph.nodes)
                    
                    if not node_exists:
                        # Add new node
                        graph.add_node(id=coactor_id, name=coactor_name)
                        # Track for next iteration
                        nodes_to_process.append((coactor_id, coactor_name))
                    
                    # Add edge (will not duplicate if already exists)
                    graph.add_edge(source=node_id, target=coactor_id)
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
        
        print(f"Iteration {iteration + 1} complete. Added {len(nodes_to_process)} new nodes")
    
    print(f"\nFinal graph: {graph.total_nodes()} nodes, {graph.total_edges()} edges")


def return_name()->str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    return 'kpalit3'


# You should modify __main__ as you see fit to build/test your graph using  the TMDBAPIUtils & Graph classes.
# Some boilerplate/sample code is provided for demonstration. We will not call __main__ during grading.

if __name__ == "__main__":

    graph = Graph()
    graph.add_node(id='2975', name='Laurence Fishburne')
    tmdb_api_utils = TMDBAPIUtils(api_key='10152dddc7d65e1fb0822dc1de34f963')

    # Build the co-actor network
    build_co_actor_network(graph, tmdb_api_utils, start_actor_id='2975')

    graph.write_edges_file()
    graph.write_nodes_file()

    # If you have already built & written out your graph, you could read in your nodes & edges files
    # to perform testing on your graph.
    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")

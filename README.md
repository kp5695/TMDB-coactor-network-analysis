# Co-Actor Network Analysis

A Python tool that builds a **co-actor network graph** using the [TMDB (The Movie Database) API](https://www.themoviedb.org/documentation/api). Starting from a given actor, it maps out who they've appeared alongside in films, then expands outward to their co-actors' co-actors — building a rich graph of Hollywood connections.

The default configuration builds a network centered on **Laurence Fishburne**, using movies released in **1999**.

---

## Features

- Fetches movie credits and cast data from the TMDB API
- Builds an undirected graph of co-actor relationships
- Expands the network iteratively (up to 2 degrees of separation)
- Exports the resulting graph to `nodes.csv` and `edges.csv` for use in visualization tools like [Gephi](https://gephi.org/) or [Cytoscape](https://cytoscape.org/)
- Supports filtering by release date range and limiting cast size per movie

---

## Project Structure

```
.
├── coactor_analysis.py   # Main script: Graph class, TMDB API utils, network builder
├── nodes.csv             # Output: actor nodes (id, name)
└── edges.csv             # Output: co-actor edges (source, target)
```

---

## Requirements

- Python 3.10+
- `requests` library

Install dependencies:

```bash
pip install requests
```

---

## Setup

1. Obtain a free API key from [TMDB](https://www.themoviedb.org/settings/api).
2. Open `coactor_analysis.py` and replace the `api_key` value in the `__main__` block:

```python
tmdb_api_utils = TMDBAPIUtils(api_key='YOUR_API_KEY_HERE')
```

---

## Usage

Run the script directly:

```bash
python coactor_analysis.py
```

This will:
1. Start with Laurence Fishburne (TMDB ID: `2975`)
2. Find all movies he appeared in during 1999
3. For each movie, collect the top 5 billed cast members
4. Expand the network two more degrees out (co-actors of co-actors)
5. Write the final graph to `nodes.csv` and `edges.csv`

### Custom Starting Actor

To build a network for a different actor, update the `__main__` block:

```python
graph = Graph()
graph.add_node(id='YOUR_ACTOR_ID', name='Actor Name')
tmdb_api_utils = TMDBAPIUtils(api_key='YOUR_API_KEY')
build_co_actor_network(graph, tmdb_api_utils, start_actor_id='YOUR_ACTOR_ID')
```

You can find an actor's TMDB ID by searching on [themoviedb.org](https://www.themoviedb.org/).

---

## Output Format

**`nodes.csv`**
| id | name |
|----|------|
| 2975 | Laurence Fishburne |
| 6384 | Keanu Reeves |
| ... | ... |

**`edges.csv`**
| source | target |
|--------|--------|
| 2975 | 6384 |
| ... | ... |

---

## Key Classes & Functions

### `Graph`
An undirected graph implementation storing nodes and edges as lists of tuples.

| Method | Description |
|--------|-------------|
| `add_node(id, name)` | Adds an actor node (no duplicates) |
| `add_edge(source, target)` | Adds an undirected co-actor edge (no duplicates) |
| `max_degree_nodes()` | Returns the node(s) with the highest number of connections |
| `write_nodes_file(path)` | Exports nodes to CSV |
| `write_edges_file(path)` | Exports edges to CSV |

### `TMDBAPIUtils`
Wrapper around the TMDB REST API.

| Method | Description |
|--------|-------------|
| `get_movie_cast(movie_id, limit, exclude_ids)` | Returns cast for a movie, with optional limit and exclusions |
| `get_movie_credits_for_person(person_id, start_date, end_date)` | Returns a person's movie credits filtered by date range |

### `build_co_actor_network(graph, tmdb_api_utils, start_actor_id)`
Orchestrates the full network build. Starts from one actor, expands two degrees out, populating the provided `Graph` object.

---

## Notes

- Only **cast roles** are considered (not crew/production roles).
- Cast members are limited to the **top 5 billed** per movie (configurable via the `limit` parameter).
- The network only includes movies with a valid `release_date` in the TMDB data.
- A small delay (`0.1s`) is added between API calls to avoid rate limiting.
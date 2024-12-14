## About

This is a project for EC504 at Boston University.  This project uses Locality-Sensitive Hashing, KD-Trees, and R-Trees to search geospatial data.  Specificaly, given latitude and longitude coordinates, the program will return zip codes near those coordinates.  It also includes an interactive app.

NOTE: Please see the submitted report for additional details about running this program.

## Running with Docker (benchmarker only)

Additional information about installing Docker can be found here: https://docs.docker.com/engine/install/

With Docker installed, run the following command from the root directory to build the image, run the container, and run the programming, printing the result to the console.

```console
docker-compose up --build
```

## Running with Python Installation (for benchmarker and interactive app)

### Dependencies

Additional information about installing Python can be found here: https://www.python.org/downloads/  

(Strongly recommend Python 3.11, though later versions will likely work as well.)

Run the following setup a virtual environment in the root directory.

Mac: 
```console
python -m venv venv
source venv/bin/activate
```

Win:
```console
python -m venv venv
venv\Scripts\activate.bat
```

Run the following to install dependencies in the virtual environment.

```console
pip install -r requirements.txt
```

### Running Program

The main entry point is the benchmark.py.  Run the following in the root directory to execute the LSH, KD-Tree, and R-Tree algorithms on some sample data (US zip codes and coordinates).  After a minute or so the program will print to the console their accuracies and run times. 

```console
python src/main.py
```

## Unit Tests

(Needs to be developed more...)

From the root run the following run all unit tests with pytest:

```console
pytest
```

## Coverage

(Need to fix...)

```console
python -m coverage run -m pytest
python -m coverage [report | html]
```

## Example output

```console
(venv) $ python src/benchmark.py
INFO:root:Approximate KD Tree - Time: 0.00023s, Accuracy: 0.07
INFO:root:Multi-Table LSH - Time: 0.03436s, Accuracy: 0.56
INFO:root:R-Tree - Time: 0.00136s, Accuracy: 0.90
```

## Contributors

Chris Krenz

## License

[MIT License](LICENSE)

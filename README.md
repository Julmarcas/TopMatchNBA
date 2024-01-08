# TopMatchNBA

TopMatchNBA is a project designed to fetch and display the latest NBA match
data in a simple and user-friendly format. The backend is written in Python
and updates a JSON file with the latest match data, which is then displayed
on a static HTML website.

## Features

- **Automated Data Fetching**: Python scripts fetch the latest NBA match data daily.
- **Static Website**: Easy-to-navigate static website displaying NBA matches.
- **JSON Data Source**: Match data is stored in a JSON file, enabling easy updates and maintenance.

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:Julmarcas/TopMatchNBA.git
   cd TopMatchNBA
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Run the Python Script:**

   ```bash
   poetry run python3 -m topmatchnba.main
   ```

   This script updates the `games.json` file in the `public` directory with the latest NBA match data.

4. **View the Website:**
   Open `public/index.html` in a web browser to view the NBA matches displayed on the website.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/TopMatchNBA/issues) if you want to contribute.

## Author

- **Julio Marquez** - _Initial work_ - [Julmarcas](https://github.com/Julmarcas)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NBA Data API
- Python Community

<div align="center">

# Four in a Row Web

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![pygame-ce](https://img.shields.io/badge/Library-pygame--ce-1D9BF0?logo=pygame&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Web-lightgrey)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
[![Deploy to Web](https://github.com/ShivamKR12/four-in-a-row/actions/workflows/pygbag.yml/badge.svg)](https://github.com/ShivamKR12/four-in-a-row/actions/workflows/pygbag.yml)
![License](https://img.shields.io/badge/License-MIT-green.svg)

</div>

A browser-ready implementation of the classic Connect Four game built with Python and Pygame Community Edition. Drop your discs and connect four in a row to win, playable directly in your browser via WebAssembly and Pygbag!

## 🚀 Features

*   Classic Four-in-a-Row gameplay mechanics.
*   Web-ready deployment out of the box.
*   Clean, colorful Pygame-CE graphics.
*   Playable directly in the browser!

## 🎮 Getting Started

You can easily play the game online or run it locally on your computer.

1.  Go to the [**GitHub Pages**](https://ShivamKR12.github.io/four-in-a-row/) to play directly in your browser.
2.  Wait for the WebAssembly to load, and enjoy!

## 🕹️ How to Play

*   **Mouse Click:** Drop a disc into the column where your cursor is hovering.
*   **Goal:** Be the first to connect four of your discs horizontally, vertically, or diagonally.

## 🛠️ Building From Source

If you want to run the game natively or compile it yourself, you'll need Python 3 and some dependencies.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/ShivamKR12/four-in-a-row.git
    cd four-in-a-row
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```sh
    pip install pygame-ce pygbag
    ```

4.  **Run natively:**
    ```sh
    python main.py
    ```

5.  **Build for the web locally:**
    This project uses Pygbag to run Pygame on the web.
    ```sh
    pygbag main.py
    ```
    Navigate to `http://localhost:8000` to test it in your browser!

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

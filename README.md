# Hand written Digit Recognition Machine Learning Model
An AI model that recognizes hand written digits, trained with the [MNIST](https://www.kaggle.com/datasets/hojjatk/mnist-dataset) dataset, with more than 99,56% accuracy.

## Instructions
The project is written in Python using Jupyter Notebook and CUDA programming lanuage through tensorflow. It can be run both on google colabs or locally.

### Prerequisites (local execution)
- CUDA Toolkit installed on your system
- A compatible NVIDIA GPU
- UNIX based system (or WSL for windows 10 and 11)

#### Building the model
1. Check the current version of the CUDA toolkit installed on your machine (recommended version: 12.6):
```sh
nvcc --version
```

2. Clone the repository:
```sh
git clone https://github.com/NicKylis/letter_recognition.git
```

3. Compile and run all shells, using your preferable IDE.

### Prerequisites (cloud execution)
- An account on google
- Access to google Colab Pro (optional)

#### Building the model
1. Open the main.ipynb file
2. Click on the __Open in Colab__ button on the top left of the file
3. Navigate to the Execution time (runtime) menu and select Run all (Ctrl+F9)

> **Note**: Remember to adjust the number of epochs to your system's limitations. If you are using google Colabs without Colab Pro access, you might encounter very slow compilation times or even be kicked out from the session mid training. Setting the number of epochs to 10 should be sufficient for more than 96% accuracy.

## Authors
Kylintireas Nikolaos, Lourmpakis Evangelos, Toramanidou Christodouli

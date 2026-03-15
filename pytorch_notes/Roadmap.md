### Phase 1: Bridge the Gap (Learn PyTorch Basics)

Before jumping into unsupervised learning, you need to understand how PyTorch works. PyTorch doesn't have a simple `.fit()` method; you build the engine yourself.

* **Topics to cover:**
  * **Tensors:** The PyTorch equivalent of NumPy arrays (`torch.Tensor`).
  * **Autograd:** How PyTorch automatically calculates derivatives/gradients (`loss.backward()`).
  * **Building a Model:** Creating a class that inherits from `nn.Module` and defining the `forward()` pass.
  * **Data Handling:** Using `torch.utils.data.Dataset` and `DataLoader` for batching.
  * **The Training Loop:** Learn the standard 5-step loop:
        1. Forward pass (predictions)
        2. Calculate Loss
        3. Clear gradients (`optimizer.zero_grad()`)
        4. Backpropagation (`loss.backward()`)
        5. Update weights (`optimizer.step()`)
* **Action Item:** Build a simple Feed-Forward Neural Network to classify handwritten digits (MNIST dataset) just to get comfortable with PyTorch syntax.

### Phase 2: Dimensionality Reduction (The Deep Learning Way)

You likely know PCA (Principal Component Analysis) from scikit-learn. In PyTorch, the equivalent starting point for unsupervised learning is the **Autoencoder**.

* **Standard Autoencoders (AE):**
  * **Concept:** A neural network designed to compress data into a smaller "latent space" (Encoder) and then reconstruct it back to its original form (Decoder).
  * **Why it's unsupervised:** The target output is the exact same as the input data! No labels needed.
  * **Action Item:** Build an Autoencoder with Linear layers (`nn.Linear`) to compress MNIST images from 784 pixels down to 32 pixels, and then reconstruct them.
* **Convolutional Autoencoders:**
  * **Concept:** Using Convolutional Neural Networks (CNNs) inside the encoder/decoder for image data, as they are much better at handling spatial data than linear layers.
  * **Action Item:** Upgrade your standard Autoencoder using `nn.Conv2d` and `nn.ConvTranspose2d` (for decoding).
* **Denoising Autoencoders:**
  * **Concept:** Add random noise to your input images, but train the model to output the *clean* original images. It forces the model to learn the most important features of the data.

### Phase 3: Generative Unsupervised Learning

Once you can compress and reconstruct data, the next step is learning how to generate *new* data that has never existed before.

* **Variational Autoencoders (VAEs):**
  * **Concept:** Instead of compressing data into fixed points, VAEs compress data into a *probability distribution* (mean and variance). This allows you to sample random points from this distribution to generate new, fake data.
  * **Math concepts to learn:** KL-Divergence (added to your loss function) and the "Reparameterization Trick".
  * **Action Item:** Build a VAE that generates entirely new, fake handwritten digits.
* **Generative Adversarial Networks (GANs):**
  * **Concept:** Two neural networks competing against each other. A **Generator** tries to create fake images, and a **Discriminator** tries to guess if the image is real or fake. Over time, the Generator becomes an expert at forging data.
  * **Action Item:** Build a Simple GAN, and then a DCGAN (Deep Convolutional GAN) to generate realistic faces (using a dataset like CelebA) or fake numbers.

### Phase 4: Modern Unsupervised Techniques (Self-Supervised Learning)

The cutting-edge of unsupervised learning today is called **Self-Supervised Learning (SSL)**. It is heavily used in Large Language Models (like ChatGPT) and modern computer vision.

* **Pretext Tasks:**
  * **Concept:** Creating fake "labels" from unlabelled data. For example, rotating an image by 90 degrees and making the neural network predict the rotation angle. By learning to predict the rotation, the model learns what the object looks like without human labels.
* **Contrastive Learning:**
  * **Concept:** Teaching a model to recognize that two augmented versions of the *same* image (e.g., one cropped, one color-filtered) are the same, while keeping them distinct from *different* images.
  * **Algorithms to look into:** SimCLR (Simple Framework for Contrastive Learning of Visual Representations).
  * **Action Item:** Implement a basic version of SimCLR to group similar images together without ever feeding the model a single label.

### Phase 5: Unsupervised Learning on Sequences (Text/Time Series)

If you want to move away from images and into text or numbers:

* **Word Embeddings (Word2Vec):**
  * Learn how to train a Skip-Gram or CBOW model in PyTorch. This is unsupervised text learning where a word tries to predict its surrounding neighbors.
* **Recurrent Autoencoders:**
  * Using LSTMs or GRUs inside an autoencoder to compress and reconstruct time-series data (great for anomaly detection, like finding credit card fraud).

---

### 📚 Recommended Resources to Follow This Roadmap

1. **PyTorch Official Tutorials:** Start with the "Deep Learning with PyTorch: A 60 Minute Blitz" on their official website.
2. **Book:** *"Deep Learning with PyTorch"* by Eli Stevens, Luca Antiga, and Thomas Viehmann (Excellent for bridging the gap from sklearn).
3. **YouTube Channels:**
    * **Aladdin Persson:** He has incredible, line-by-line PyTorch tutorials for Autoencoders, VAEs, and GANs.
    * **StatQuest with Josh Starmer:** Great for understanding the *math* behind Neural Networks and VAEs intuitively.
4. **Dataset Hub:** Use `torchvision.datasets` (MNIST, CIFAR10, CelebA) so you don't have to worry about scraping data while learning.

**My Advice for your transition:** Don't try to learn the math and the PyTorch syntax at the exact same time. First, build a simple model in PyTorch just to get the code working. *Then*, look at the loss function and understand the math behind why it works!

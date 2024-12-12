# -*- coding: utf-8 -*-
"""WORKING GAN

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iEZCiUjTk5TOeuNkhblo7K9ka9DeCMH7
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import layers, Model, optimizers
from keras.layers import Input, Conv2D, LeakyReLU, BatchNormalization, UpSampling2D, Activation, Flatten, Dense, MaxPooling2D, Conv2DTranspose, Add, Reshape
from keras.models import Model
from keras.optimizers import Adam
import requests
from PIL import Image
import os
from sklearn.model_selection import train_test_split

# from keras.datasets import cifar10, mnist

def get_imgs(folder_path):

    # List all files in the folder
    file_names = os.listdir(folder_path)

    # Filter out only image files (assuming they have common image extensions)
    image_files = [f for f in file_names if f.endswith(('jpg', 'jpeg', 'png', 'bmp', 'gif'))]

    image_files.sort()

    # Load images into a list
    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)
        images.append(np.array(image))

    images_array = np.stack(images)

    return images_array

!git clone https://github.com/marknader11/ultrasound_denoise.git

n = 255
clean_train = get_imgs('/content/ultrasound_denoise/proper split/clean_train')/n
clean_test = get_imgs('/content/ultrasound_denoise/proper split/clean_test')/n
clean_val = get_imgs('/content/ultrasound_denoise/proper split/clean_val')/n

noisy_train = get_imgs('/content/ultrasound_denoise/proper split/noisy_train')/n
noisy_test = get_imgs('/content/ultrasound_denoise/proper split/noisy_test')/n
noisy_val = get_imgs('/content/ultrasound_denoise/proper split/noisy_val')/n

# Now 'images_array' contains all the images from the folder
plt.figure(figsize=(15, 6))
for i in range(1, 6):
    plt.subplot(2, 5, i)
    plt.imshow(clean_train[i], cmap='gray')
    plt.axis('off')
    plt.subplot(2, 5, i+5)
    plt.imshow(noisy_train[i], cmap='gray')
    plt.axis('off')
plt.show()

def conv_block(x,layers):
  x = Conv2D(layers, (3, 3), padding='same')(x)
  x = LeakyReLU(alpha=0.2)(x)
  # x = BatchNormalization(momentum=0.8)(x)
  x = Conv2D(layers, (3, 3), padding='same')(x)
  x = LeakyReLU(alpha=0.2)(x)
  # x = BatchNormalization(momentum=0.8)(x)

  return x

def de_conv_block(x,layers):
  x = Conv2DTranspose(layers, (4, 4), strides=(2, 2), padding='same')(x)
  x = LeakyReLU(alpha=0.2)(x)
  # x = BatchNormalization(momentum=0.8)(x)
  return x

def build_generator(): #meh
    input_img = Input((512,512, 1))

    x = Reshape((512, 512, 1))(input_img)
    size = 32

    x = conv_block(x, int(size))
    skip1 = x
    x = MaxPooling2D(pool_size=(4, 4), strides=(2, 2), padding = 'same')(x)

    x = conv_block(x, int(size*2))
    skip2 = x
    x = MaxPooling2D(pool_size=(4, 4), strides=(2, 2), padding = 'same')(x)

    x = conv_block(x, int(size*4))
    skip3 = x
    x = MaxPooling2D(pool_size=(4, 4), strides=(2, 2), padding = 'same')(x)

    x = conv_block(x, int(size*8))
    skip4 = x
    x = MaxPooling2D(pool_size=(4, 4), strides=(2, 2), padding = 'same')(x)
    x = conv_block(x, int(size*16))

    x = de_conv_block(x, int(size*8))
    x = Add()([x, skip4])

    x = de_conv_block(x, int(size*4))
    x = Add()([x, skip3])

    x = de_conv_block(x, int(size*2))
    x = Add()([x, skip2])

    x = de_conv_block(x, int(size))
    x = Add()([x, skip1])

    x = Conv2D(1, (1, 1), padding='same')(x)
    # output_img = Activation('tanh')(x)

    return Model(input_img, x)

generator = build_generator()
generator.summary()

def build_discriminator():
  input_img = Input((512,512, 1))
  size = 32

  x = Conv2D(int(size), (4, 4), strides=(2, 2), padding='valid')(input_img)
  x = LeakyReLU(alpha=0.2)(x)

  x = Conv2D(int(size*2), (4, 4), strides=(2, 2), padding='valid')(x)
  x = BatchNormalization(momentum=0.8)(x)
  x = LeakyReLU(alpha=0.2)(x)

  x = Conv2D(int(size*4), (4, 4), strides=(2, 2), padding='valid')(x)
  x = BatchNormalization(momentum=0.8)(x)
  x = LeakyReLU(alpha=0.2)(x)

  x = Conv2D(int(size*8), (4, 4), strides=(2, 2), padding='valid')(x)
  x = BatchNormalization(momentum=0.8)(x)
  x = LeakyReLU(alpha=0.2)(x)

  x = Conv2D(1, (1, 1), padding='valid')(x)
  x = Flatten()(x)
  x = Dense(16)(x)
  x = Dense(16)(x)
  x = Dense(1)(x)
  pred = Activation('sigmoid')(x)
  return Model(input_img, pred)

discriminator = build_discriminator()
discriminator.summary()

def ssim_metric(y_true, y_pred):
    return tf.reduce_mean(tf.image.ssim(y_true, y_pred, max_val=1.0))

def PSNR_metric(y_true,y_pred,max_pixel=1.0):
    # Calculate Mean Squared Error (MSE)
    mse = tf.reduce_mean(tf.square(y_true - y_pred), axis=[-3, -2, -1])

    # Handle potential division by zero
    mse = tf.maximum(mse, 1e-10)

    # Calculate PSNR
    # PSNR = 10 * log10((MAX^2) / MSE)
    psnr = 10.0 * tf.math.log(max_pixel**2 / mse) / tf.math.log(10.0)
    return tf.reduce_mean(psnr)



epochs = 100
BATCH_SIZE = 15
DATASET_SIZE = noisy_train.shape[0]
TRAIN_EVERY_N_EPOCH = 5
WARM_UP_DISC_EPOCHS = 20

# save_interval = 25
# image_interval = 5

valid_labels = np.ones((BATCH_SIZE, 1))
fake_labels = np.zeros((BATCH_SIZE, 1))
labels = tf.concat((fake_labels, valid_labels), axis=0)
labels = tf.squeeze(labels)


acc_metric = tf.keras.metrics.BinaryAccuracy()
disc_optim = Adam()
gen_optim = Adam()
bce = tf.keras.losses.BinaryCrossentropy(from_logits=False)
mse = tf.keras.losses.MeanSquaredError()
acc_metric = tf.keras.metrics.Accuracy()

generator = build_generator()
discriminator = build_discriminator()


for epoch in range(epochs):
  for _ in range(DATASET_SIZE//BATCH_SIZE):
    idx = np.random.randint(0, noisy_train.shape[0], BATCH_SIZE)
    noisy_imgs = noisy_train[idx]
    clean_imgs = clean_train[idx]
    clean_imgs = tf.cast(clean_imgs, dtype=tf.float32) # Cast clean_imgs to float32

    # We keep all the gradients of anything here
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape: # Separate tapes for generator and discriminator
      # Generate images
      gen_imgs = generator((noisy_imgs))
      gen_imgs = tf.squeeze(gen_imgs)
      imgs = tf.concat((gen_imgs, clean_imgs), axis=0)

      pred_labels = discriminator(imgs)
      pred_labels = tf.squeeze(pred_labels)


      loss = bce(pred_labels, labels)
      mse_loss = mse(gen_imgs,clean_imgs)

      if epoch > WARM_UP_DISC_EPOCHS:
        gen_gradients = gen_tape.gradient((2000*mse_loss)-loss, generator.trainable_variables)
        gen_optim.apply_gradients(zip(gen_gradients, generator.trainable_variables))

      if epoch < WARM_UP_DISC_EPOCHS or epoch % TRAIN_EVERY_N_EPOCH == 0:
        disc_gradients = disc_tape.gradient(loss, discriminator.trainable_variables)
        disc_optim.apply_gradients(zip(disc_gradients, discriminator.trainable_variables))
        disc_acc = acc_metric(pred_labels, labels)

  gen_acc = ssim_metric(clean_imgs,gen_imgs)
  print(f"{epoch} disc_acc is {disc_acc} gen_acc is {gen_acc}")

# generator.save_weights('generator_weights.weights.h5')

# Test the generator with noisy test images
BATCH_SIZE = 5
idx = np.random.randint(0, clean_test.shape[0], BATCH_SIZE)
clean_test_batch = clean_test[idx]
noisy_test_batch = noisy_test[idx]
gen_test_batch = generator.predict(noisy_test_batch)

clean_test_batch = tf.expand_dims(clean_test[idx],-1)
noisy_test_batch = tf.expand_dims(noisy_test[idx],-1)

clean_test_batch = tf.cast(clean_test_batch, tf.float32)
noisy_test_batch = tf.cast(noisy_test_batch, tf.float32)



# x_baseline = tf.cast(noisy_test_batch, tf.float32)
# x_baseline = tf.expand_dims(x_baseline,-1)
# y_baseline = tf.cast(clean_test_batch, tf.float32)
# y_baseline = tf.expand_dims((y_baseline),-1)


print('Baseline  SSIM is: ', ssim_metric(clean_test_batch, noisy_test_batch))
print('Resulting SSIM is: ', ssim_metric(clean_test_batch, gen_test_batch))
print('')
print('Baneline  PSNR is: ', PSNR_metric(clean_test_batch, noisy_test_batch))
print('Resulting PSNR is: ', PSNR_metric(clean_test_batch, gen_test_batch))
print('')

# Plot the results
mod = -1

plt.figure(figsize=(10, 6))
for i in range(1, 6):
    plt.subplot(3, 5, i)
    plt.imshow(clean_test_batch[i+mod], cmap='gray')
    plt.axis('off')
    plt.subplot(3, 5, i+5)
    plt.imshow(noisy_test_batch[i+mod], cmap='gray')
    plt.axis('off')
    plt.subplot(3, 5, i+10)
    plt.imshow(gen_test_batch[i+mod], cmap='gray')
    plt.axis('off')
plt.show()

ct_test_1 = Image.open('/content/aln_us_test_3.jpg').convert('L')
ct_test_1 = ct_test_1.resize((512, 512))
ct_test_1 = np.array(ct_test_1)
ct_test_1 = ct_test_1/n

ct_test_1 = tf.expand_dims(ct_test_1, axis=0)


us_test_1 = (generator(ct_test_1))
us_test_1 = tf.cast(us_test_1*255, tf.uint8)
us_test_1 = tf.squeeze(us_test_1)
us_test_1 = tf.expand_dims(us_test_1, axis=-1)
tf.io.write_file('us_test_3.jpeg', tf.image.encode_jpeg(us_test_1, quality=100, format='grayscale'))
us_test_1 = tf.squeeze(us_test_1)


plt.imshow(us_test_1, cmap='gray')
plt.axis('off')

# plt.figure(figsize=(10, 6))
# for i in range(1, 6):
#     plt.subplot(3, 5, i)
#     plt.imshow(clean_test_batch[i+mod], cmap='gray')
#     plt.axis('off')
#     plt.subplot(3, 5, i+5)
#     plt.imshow(noisy_test_batch[i+mod], cmap='gray')
#     plt.axis('off')
#     plt.subplot(3, 5, i+10)
#     plt.imshow(gen_test[i+mod], cmap='gray')
#     plt.axis('off')
# plt.show()

# save_path  = '/content/ultrasound_denoise/results/'
# if  not os.path.exists(save_path):
#   os.mkdir(save_path)
# save_folder = save_path + 'base_gan/'
# if not os.path.exists(save_folder):
#   os.mkdir(save_folder)

# c_folder = save_folder + 'clean/'
# n_folder = save_folder + 'noisy/'
# g_folder = save_folder + 'gen/'

# if not os.path.exists(c_folder):
#   os.mkdir(c_folder)
# if not os.path.exists(n_folder):
#   os.mkdir(n_folder)
# if not os.path.exists(g_folder):
#   os.mkdir(g_folder)

# save_clean = tf.expand_dims(clean_test_batch, axis=-1)
# save_noisy = tf.expand_dims(noisy_test_batch, axis=-1)


# save_clean = tf.cast(clean_test_batch*255, tf.uint8)
# save_noisy = tf.cast(noisy_test_batch*255, tf.uint8)
# save_gen = tf.cast(gen_test_batch*255, tf.uint8)




# for i in range(save_clean.shape[0]):
#   clean_img = tf.image.encode_jpeg(save_clean[i], quality=100, format='grayscale')
#   noisy_img = tf.image.encode_jpeg(save_noisy[i], quality=100, format='grayscale')
#   gen_img = tf.image.encode_jpeg(save_gen[i], quality=100, format='grayscale')

#   tf.io.write_file(c_folder + f'clean_img_{i}.jpeg',clean_img,)
#   tf.io.write_file(n_folder + f'noisy_img_{i}.jpeg',noisy_img)
#   tf.io.write_file(g_folder + f'gen_img_{i}.jpeg',gen_img)

# Commented out IPython magic to ensure Python compatibility.
def git_push():
  !git config --global user.name "marknader11"
  !git config --global user.email "mark.nader2000@gmail.com"
  !git remote set-url origin https://marknader11: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@github.com/marknader11/ultrasound_denoise.git

#   %cd /content/ultrasound_denoise/
#   %ls
  !git add .
  !git commit -m "added results base"
  !git push origin main

git_push()
addpath("test_set\")


test_ct(:,:,1) = im2double((imread("ct_test_1.jpg")));
test_ct(:,:,2) = im2double(imread("ct_test_2.jpg"));
test_ct(:,:,3) = im2double(imread("ct_test_3.jpg"));


test_us(:,:,1) = im2double(imread("us_test_1.jpg"));
test_us(:,:,2) = im2double(imread("us_test_2.jpg"));
test_us(:,:,3) = im2double(imread("us_test_3.jpg"));

for i = 1:3
    img1 = test_ct(:,:,i);
    img2 = test_us(:,:,i);

    sigma = 10; % Standard deviation of the Gaussian kernel
    filteredImg = imgaussfilt(img2, sigma);

    % Compute 2D cross-correlation
    correlation = normxcorr2(img1, filteredImg);
    
    % Find the peak correlation location
    [max_corr, max_index] = max(correlation(:));
    [y_peak, x_peak] = ind2sub(size(correlation), max_index);
    
    % Calculate the shift
    x_shift = x_peak - size(img1, 2);
    y_shift = y_peak - size(img1, 1);
    
    % Create output shift vector
    shift = [x_shift, y_shift];
    
    % Perform image shifting
    aligned_image(:,:,i) = imtranslate(img2, -shift);
    imshow(imtranslate(img2, -shift))
end
%%
figure()
subplot(1,3,1)
imshow(test_ct(:,:,2))
subplot(1,3,2)
imshow(test_us(:,:,2))
subplot(1,3,3)
imshow(aligned_image(:,:,2))


%%

clean_imgs = test_ct;
noisy_imgs = aligned_image;

im1path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\base_split_tune\gen_test_1.jpeg';
im2path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\base_split_tune\gen_test_2.jpeg';
im3path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\base_split_tune\gen_test_3.jpeg';

gan1path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\gan\us_test_1.jpeg';
gan2path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\gan\us_test_2.jpeg';
gan3path = 'G:\OneDrive - Cal Poly\Master Thesis\Thesis Document and Data\test_set\gan\us_test_3.jpeg';

gen_imgs(:,:,1) = im2double(imread(im1path));
gen_imgs(:,:,2) = im2double(imread(im2path));
gen_imgs(:,:,3) = im2double(imread(im3path));

gan_imgs(:,:,1) = im2double(imread(gan1path));
gan_imgs(:,:,2) = im2double(imread(gan2path));
gan_imgs(:,:,3) = im2double(imread(gan3path));

%%
for i = 1:3
    gen_imgs(:,:,i) = (gen_imgs(:,:,i)/ max(gen_imgs(:,:,i),[],'all'));
    gan_imgs(:,:,i) = imgaussfilt((gan_imgs(:,:,i)/ max(gan_imgs(:,:,i),[],'all')),0.5);
end

%% BM3D
[bm3d_imgs, bm3d_std] = get_bm3d(clean_imgs,noisy_imgs);
%% LEE filt

for j = 1: size(aligned_image,3)
    kern = rktkern();
    [out,~,~] = rktfilt(aligned_image(:,:,j),kern,'mix');
    lee(:,:,j) = (aligned_image(:,:,j)-out);
end

%% Specklefilt
for j = 1: size(aligned_image,3)
    matlab_filt(:,:,j) = specklefilt(aligned_image(:,:,j), "NumIterations",50);
end 
%%
for i = 1:size(test_ct,3)
    baseline_PSNR(i) = psnr(noisy_imgs(:,:,i),clean_imgs(:,:,i));
    model_PSNR(i) = psnr(gen_imgs(:,:,i),clean_imgs(:,:,i));
    gan_PSNR(i) = psnr(gan_imgs(:,:,i),clean_imgs(:,:,i));
    bm3d_PSNR(i) = psnr(bm3d_imgs(:,:,i),clean_imgs(:,:,i));
    lee_PSNR(j) = psnr(lee(:,:,j),test_ct(:,:,j));
    
    baseline_SSIM(i) = ssim(noisy_imgs(:,:,i),clean_imgs(:,:,i));
    model_SSIM(i) = ssim(gen_imgs(:,:,i),clean_imgs(:,:,i));
    gan_SSIM(i) = ssim(gan_imgs(:,:,i),clean_imgs(:,:,i));
    bm3d_SSIM(i) = ssim(bm3d_imgs(:,:,i),clean_imgs(:,:,i));
    lee_SSIM(j) = ssim(lee(:,:,j),test_ct(:,:,j));
end
%%
j = 3;
figure()
subplot(1,2,1)
imshow(bm3d_imgs(:,:,j))
subplot(1,2,2)
imshow(gan_imgs(:,:,j))
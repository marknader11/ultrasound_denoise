target = 'base_with_split\';
[clean_imgs, noisy_imgs,gen_imgs] = get_imgs(target);

%%
tic
[bm3d_imgs] = get_bm3d(clean_imgs,noisy_imgs);
toc
%%
tic
for j = 1: size(clean_imgs,3)
    kern = rktkern();
    [out,~,~] = rktfilt(noisy_imgs(:,:,j),kern,'mix');
    lee(:,:,j) = (noisy_imgs(:,:,j)-out);
end
toc
%%
tic
for j = 1: size(clean_imgs,3)
    matlab_filt(:,:,j) = specklefilt(noisy_imgs(:,:,j), "NumIterations",50);
end 
toc
%%
for j = 1: size(clean_imgs,3)
     speck_PSNR(j) = psnr(matlab_filt(:,:,j),clean_imgs(:,:,j));
     speck_SSIM(j) = ssim(matlab_filt(:,:,j),clean_imgs(:,:,j));
end

speck_PSNR_avg = mean(speck_PSNR)
speck_SSIM_avg = mean(speck_SSIM)
%%
j = 17;
figure()
subplot(2,2,1)
imshow(clean_imgs(:,:,j))
title('Clean Image')
subplot(2,2,2)
imshow(noisy_imgs(:,:,j))
title('Ultrasound noise Image')
subplot(2,2,3)
imshow(gen_imgs(:,:,j))
title('AI Model Denoise')
% imshow(bm3d_imgs(:,:,j))
% title('BM3D Denoise')
subplot(2,2,4)
imshow(bm3d_imgs(:,:,j))
title('BM3D Denoise')
% imshow(matlab_filt(:,:,j))
% title('MATLAB Denoise')
%%
j = 64;
figure()
subplot(1,2,1)
imshow(noisy_imgs(:,:,j))
title('Ultrasound noise Image')
subplot(1,2,2)
imshow(matlab_filt(:,:,j))
title('MATLAB Denoise')
%%

j = 1;
figure()
subplot(1,3,1)
imshow(clean_imgs(:,:,j))
title('Clean Image')
subplot(1,3,2)
imshow(noisy_imgs(:,:,j))
title('Ultrasound noise Image')
subplot(1,3,3)
% imshow(bm3d_imgs(:,:,j))
% title('BM3D Denoise')
imshow(lee(:,:,j))
title('Lee Denoise')

%%

for i = 1:size(clean_imgs,3)
    baseline_PSNR(i) = psnr(noisy_imgs(:,:,i),clean_imgs(:,:,i));
    model_PSNR(i) = psnr(gen_imgs(:,:,i),clean_imgs(:,:,i));
    bm3d_PSNR(i) = psnr(bm3d_imgs(:,:,i),clean_imgs(:,:,i));
    lee_PSNR(i) = psnr(lee(:,:,i),clean_imgs(:,:,i));

    baseline_SSIM(i) = ssim(noisy_imgs(:,:,i),clean_imgs(:,:,i));
    model_SSIM(i) = ssim(gen_imgs(:,:,i),clean_imgs(:,:,i));
    bm3d_SSIM(i) = ssim(bm3d_imgs(:,:,i),clean_imgs(:,:,i));
    lee_SSIM(i) = ssim(lee(:,:,i),clean_imgs(:,:,i));
end

baseline_PSNR_avg = mean(baseline_PSNR)
model_PSNR_avg = mean(model_PSNR)
bm3d_PSNR_avg = mean(bm3d_PSNR)
lee_PSNR_avg = mean(lee_PSNR)

baseline_SSIM_avg = mean(baseline_SSIM)
model_SSIM_avg = mean(model_SSIM)
bm3d_SSIM_avg = mean(bm3d_SSIM)
lee_SSIM_avf = mean(lee_SSIM)

%%
j = 69;

figure();
% Create a 2x2 tiled layout with minimal padding and spacing
tiledlayout(2, 2, 'Padding', 'compact', 'TileSpacing', 'compact');

% Plot the Clean Image
nexttile;
imshow(clean_imgs(:, :, j));
title('Clean Image');
xlabel('PSNR: Inf   SSIM: 1.0000'); % Static values for clean image (PSNR = Inf, SSIM = 1)

% Plot the Noisy Image
nexttile;
imshow(noisy_imgs(:, :, j));
title('Ultrasound Noise Image');
xlabel(['PSNR: ', num2str(baseline_PSNR(j), '%.2f'), '   SSIM: ', num2str(baseline_SSIM(j), '%.4f')]);

% Plot the AI Model Denoise Image
nexttile;
imshow(lee(:, :, j));
title('Lee Denoise');
xlabel(['PSNR: ', num2str(lee_PSNR(j), '%.2f'), '   SSIM: ', num2str(lee_SSIM(j), '%.4f')]);

% Plot the BM3D Denoise Image
nexttile;
imshow(bm3d_imgs(:, :, j));
title('BM3D Denoise');
xlabel(['PSNR: ', num2str(bm3d_PSNR(j), '%.2f'), '   SSIM: ', num2str(bm3d_SSIM(j), '%.4f')]);





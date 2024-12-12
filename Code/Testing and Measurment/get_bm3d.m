
function [bm3d_imgs, bm3d_imgs_std] = get_bm3d(clean,noisy)
    addpath('bm3d\')


    bm3d_imgs = zeros(size(clean));
%     bm3d_avg_imgs = zeros(size(clean));

    for i = 1:size(clean,3)
        y = clean(:,:,i);
        x = noisy(:,:,i);
        noise = x - y;
        psd = abs(fft2(noise)).^2;
        y_bm3d = BM3D(x,psd);


        blur = imgaussfilt(x,20);
        noise_std = x-blur;
        y_bm3d_std = BM3D(x,noise_std);

        bm3d_imgs(:,:,i) = y_bm3d;
        bm3d_imgs_std(:,:,i) = y_bm3d_std;
%         bm3d_avg_imgs(:,:,i) = BM3D(x,train_psd);
    end
end
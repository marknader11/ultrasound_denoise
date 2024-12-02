function images = readJPGImagesFromFolder(folderPath)
    % READJPGIMAGESFROMFOLDER Reads all .jpg images from a specified folder.
    %
    %   images = READJPGIMAGESFROMFOLDER(folderPath)
    %   Reads all .jpg images from the folder specified by folderPath and
    %   returns them in a cell array.

    % Validate the folder path
    if ~isfolder(folderPath)
        error('The specified folder does not exist: %s', folderPath);
    end

    % Get a list of all .jpg files in the folder
    imageFiles = dir(fullfile(folderPath, '*.jpg'));
    
    % Initialize a cell array to store the images
    images = zeros(512,512,length(imageFiles));
    
    % Loop through the files and read the images
    for i = 1:length(imageFiles)
        imgPath = fullfile(folderPath, imageFiles(i).name); % Full path of the image
        img = double(imread(imgPath))/255; % Read the image
        images(:,:,i) = img; % Store the image in the cell array
    end

    % Display a message if no images are found
    if isempty(images)
        warning('No .jpg files found in the folder: %s', folderPath);
    else
        fprintf('Successfully loaded %d .jpg images from folder: %s\n', length(images), folderPath);
    end
end

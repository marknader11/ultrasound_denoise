tic
numJobs = 6; % Number of concurrent runs
jobs = cell(1, numJobs); % Cell array to store job objects

% Start 6 batch jobs
for i = 1:numJobs
%     pause(5)
    jobs{i} = batch('sim_kidney');
    pause(2)
end
% 
% % Wait for all jobs to complete
% for i = 1:numJobs
%     wait(jobs{i}); % Wait for each job to finish
% end
% 
% % Clean up by deleting all jobs
% for i = 1:numJobs
%     delete(jobs{i});
% end
% toc

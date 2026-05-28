function [meanValue, ciWidth] = logNormalStats(data)
    % logNormalStats 计算对数正态分布的期望均值和95%置信区间
    % 输入:
    %   data - 一列正值数据
    % 输出:
    %   meanValue - 对数正态分布的期望均值
    %   ci - 95%置信区间（以列向量形式返回）

    % 对数据进行对数变换
    log_data = log(data);

    % 计算对数变换数据的均值和标准差
    mu_log = mean(log_data);
    sigma_log = std(log_data);
    se=sigma_log/sqrt(length(log_data));
    
    % 计算95%置信区间的对数变换
    
    z=1.96;
    ciWidth = 2*z*se;

    % 计算对数正态分布的期望均值
    meanValue = exp(mu_log + (sigma_log^2) / 2);
end
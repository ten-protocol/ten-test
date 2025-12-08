// @ts-ignore
module.exports = async ({getNamedAccounts, deployments}) => {
    const {deploy} = deployments;
    const {app_developer1, app_developer2} = await getNamedAccounts();

    const double = await deploy('Double', {
        from: app_developer1,
        args: [],
        log: true,
    });

    const triple = await deploy('Triple', {
        from: app_developer2,
        args: [],
        log: true,
    });
};
module.exports.tags = ['Double', 'Triple'];
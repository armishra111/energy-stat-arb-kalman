An ever evolving python-pipeline to compare rolling OLS and Dynamic Kalman-Filter model to analyze the regime shift in 
Chevron and Exxon CVX/XOM pair trading in interest of strait of hormuz built crisis. 
This is a basic implementation of equity stat-arb model analyzing cointergration and betting on mean-reversion when signals
deviate from a given model at +-2\sigma.

Rolling OLS: y_t = \beta_0 + \beta_1*x_t + \eps_t
Kalman: y_t = \beta_0(t) + \beta_1(t) * x_t + \eps_t
Spread: s_t = \eps_t i.e y^hat_t - y_t; where |z-score(s_t)| <= 2 the model deviates and one longs/shorts the equity.
Kalman model has evolving \beta with time built with measurement (R) and process(Q) noise which evolve \beta pertaining
to stress in the market.

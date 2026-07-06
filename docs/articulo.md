Computational Economics
https://doi.org/10.1007/s10614-021-10117-6

# Analytically Pricing European Options under a New Two-Factor Heston Model with Regime Switching

Sha Lin¹ · Xin-Jiang He²

Accepted: 5 April 2021

© The Author(s), under exclusive licence to Springer Science+Business Media, LLC, part of Springer Nature 2021

## Abstract

In this paper, we propose a new two-factor stochastic volatility model by introducing a regime switching factor into the Heston model. Despite the complicated model structure, we still manage to derive a closed-form pricing formula for European options, which can save us a lot of time in option pricing and model calibration. The results of our empirical study further indicate that our model is able to provide better performance over existing ones when real market data is employed, demonstrating its possible practical applications.

**Keywords** Stochastic volatility · Two-factor · Regime switching · Closed-form · Empirical study

## 1 Introduction

In 1973, an innovative option pricing model was proposed by Black and Scholes (1973), in which the underlying price is assumed to follow a log-normal distribution, and European option prices can be obtained with a closed-form formula. This model is very popular especially among market practitioners since its analytical pricing formula can be easily implemented in real markets. However, despite its popularity, it is widely acknowledged that the Black–Scholes (B–S) model is not enough when modeling the underlying price, which is caused by some simplified assumptions made to achieve analytical tractability. A typical example is the constant volatility assumption being at odds with the phenomenon of “volatility

✉ Xin-Jiang He
xinjiang@zjut.edu.cn

¹ School of Finance, Zhejiang Gongshang University, Hangzhou, China

² School of Economics, Zhejiang University of Technology, Hangzhou, China

Published online: 01 May 2021

Springer

S. Lin, X.-J. He

smile" (Dumas et al. 1998), which is the main reason that leads to the development of various non-constant volatility models.

In the literature, non-constant volatility models can mainly be divided into two categories, i.e., local volatility and stochastic volatility models. The former was proposed by Dupire (1994), who made the volatility a deterministic function of the underlying price and time, and derived the so-called Dupire formula for the determination of the local volatility function. However, apart form the fact that the direct implementation of the Dupire formula can not yield stable results (Kamp 2009), Hagan et al. (2002) even pointed out that "smile dynamics" are poorly captured by local volatility models. Therefore, much more attention has been paid to the latter category of stochastic volatility models.

In fact, stochastic volatility models are formed by making volatility another random variable in addition to the underlying price, and a number of authors have worked on the option pricing problem under stochastic volatility models. However, it needs to be pointed out that it actually becomes very difficult to find a closed-form pricing formula for European options after the introduction of another stochastic source, and numerical methods must be resorted to for most of existing models. For example, Scott (1987) and Wiggins (1987) adopted the Monte Carlo simulation and finite difference method respectively to find option prices. Unfortunately, those models without an analytical pricing formula can hardly be applied in real markets since it will take a large amount of time when model calibration and option valuation. As a result, a large amount of research interest has been led into establishing stochastic volatility models with closed-form solutions. In particular, Hull and White (1987) derived a series solution under their adopted model with the volatility following another geometric Brownian motion. But, this model is still not satisfactory since the assumption of independence between the underlying price and the volatility violates the leverage effects that the volatility and the underlying price are actually negatively related according to many empirical studies (Bakshi et al. 1997; Jacquier et al. 2004). Fortunately, Heston (1993) proposed an elegant model that it not only has incorporated some nice features for the volatility process, such as the non-negative property and the mean-reverting property being consistent with real market observations, but also possesses a closed-form pricing formula, which can certainly save us a lot of time and effort in its implementation. Despite the great success of the Heston model, it also suffers from some problems, as the Heston model with constant parameters may not provide good fitness to market data.

In this situation, time-dependent parameters are introduced into the Heston model when option pricing (Mikhailov and Nögel 2003), while the parameters in the volatility process of the Heston model are even made to be stochastic variables (Kaeck and Alexander 2010). Furthermore, a lot of empirical evidence has suggested that incorporating regime switching into the volatility process will provide better performance in real markets. For example, Kalimipalli and Susmel (2004) modeled the short-term interest rate with a regime switching stochastic volatility model, the results of which show that there can be better in-sample performance compared with those models without regime switching. Moreover, Vo (2009) found strong empirical evidence of regime switching in real markets that regime switching stochastic volatility models can not only enhance the forecasting

Analytically Pricing European Options under a New...

power of the stochastic volatility model, but also better capture major events affecting the market.

In order to capture the effect of regime switching in the volatility process while still preserve the analytical tractability, we propose a new regime switching stochastic volatility model in this paper, with the volatility following a two-factor stochastic process; one is the same as that in the Heston model, and another is governed by a Markov chain. Our motivation can mainly be summarized from two aspects. On one hand, such a modification to the Heston model does not break down the analytical tractability. This is an essential advantage of our model as the model calibration process is very time consuming and the availability of an analytical pricing formula ensures the computational efficiency, which is vital for its practical applications. On the other hand, modeling stochastic volatility with multiple stochastic factors are becoming increasingly popular, as this could yield better fitness to real market data (Christoffersen et al. 2009; Pacati et al. 2014, 2018). In particular, He and Zhu (2016) recently proposed a regime switching Heston model by allowing the volatility of volatility in the Heston model to jump between different states following a Markov chain. Although their empirical results demonstrated the superiority of their model over the Heston model in their tested sets of data, they only provided an analytical approximation formula, which is suitable for short-tenor options. This has prompted us to try to construct a model that incorporates regime switching in the volatility of volatility and at the same time admits an analytical solution.

Of course, the complicated model structure makes the direct derivation of the characteristic function under this particular model especially very difficult to achieve, and thus we go through a two-step process that in the first step, we work out the characteristic function of the underlying price conditional upon all the future information of the Markov chain. By doing so, the unconditional characteristic function to be derived in the second step is actually the expectation of the conditional characteristic function with respect to the Markov chain, based on which a closed-form pricing formula for European options is successfully obtained. Numerical experiments are then carried out to show the accuracy and various properties of the newly derived pricing formula. Finally, we conduct an empirical study to demonstrate the importance of including a regime switching factor for the volatility of volatility. It should be remarked that although there exist a number of different stochastic volatility models (Heston 1993; Hagan et al. 2002), only a few attempts have been made in the literature (Elliott and Lian 2013; He and Zhu 2016) to introduce regime switching into stochastic volatility processes when pricing financial derivatives. Clearly, our model is different from the Elliott–Lian model (Elliott and Lian 2013) since they made the mean reversion level of the Heston model regime switching, and one can also distinguish our work from that presented by He and Zhu (2016), as they were only able to derive an approximation formula when considering a regime switching volatility of volatility.

The rest of the paper is organized as follows. In Sect. 2, we will first briefly introduce our new stochastic volatility model, and then the European option pricing problem is divided into two stages; in the first stage, the conditional characteristic function of the underlying price is obtained, based on which the unconditional

Springer

S. Lin, X.-J. He

characteristic function as well as the pricing formula is provided. In Sect. 3, numerical experiments are carried out to show the accuracy of our pricing formula and the difference between our model and the Heston model. In Sect. 4, an empirical study is carried out to show whether it is meaningful to introduce regime switching with our approach, followed by some concluding remarks given in the last section.

## 2 Closed-Form Solution

In this section, we propose a new stochastic volatility model for the dynamics of the underlying price and the volatility that can better capture the characteristics exhibited by real market data. In particular, the underlying price in the newly proposed model follows a geometric Brownian motion, and the volatility follows a two-factor process, which is constructed with the mean-reverting CIR (Cox–Ingersoll–Ross) model as one factor and another factor controlled by a Markov chain. The derivation process of the closed-form pricing formula for European options is then presented under the newly proposed model.

### 2.1 A New Stochastic Volatility Model

As discussed above, a lot of empirical evidence has already suggested the existence of regime switching in the volatility process (Kalimipalli and Susmel 2004; Vo 2009), and it was even demonstrated by He and Zhu (2016) that a regime switching volatility of volatility could provide better model performance. Being aware of this, we now propose a new stochastic volatility model, under which the underlying price $S_t$ and the volatility $v_t$ under a risk-neutral measure are assumed to follow a geometric Brownian motion

$$\frac{dS_t}{S_t} = rdt + \sqrt{v_t}dW_t^1, \tag{2.1}$$

and a two-factor volatility process¹

$$dv = k(\theta - v)dt + \sigma\sqrt{v}dW_t^2 + \lambda_{X_t}dB_t, \tag{2.2}$$

respectively. Here, $r$ represents the risk-free interest rate, and $W_t^1$ and $W_t^2$ are two standard Brownian motions with correlation $\rho$. $B_t$ is another Brownian motion independent of $W_t^1$, $W_t^2$. $X_t$ is a Markov chain, independent of the two Brownian motions, and it is defined as²

¹ Being different from the two-factor fuzzy time series (Abhishekh et al. 2019; Abhishekh and Kumar 2019), two-factor stochastic processes are referred to as those that are constructed with two diffusion terms.

² For illustration purposes, we assume that $X_t$ is constructed with two states, but the extension to arbitrary but finite states is very straightforward.

Analytically Pricing European Options under a New...

$$X _ { t } = \left\{ \begin{array} { l l } { ( 1 , 0 ) ^ { T } , } & { \mathrm { w h e n ~ t h e ~ e c o n o m y ~ i s ~ b e l i e v e d ~ t o ~ b e ~ i n ~ S t a t e ~ 1 } , } \\ { ( 0 , 1 ) ^ { T } , } & { \mathrm { w h e n ~ t h e ~ e c o n o m y ~ i s ~ b e l i e v e d ~ t o ~ b e ~ i n ~ S t a t e ~ 2 } . } \end{array} \right.$$

Here, the transition between the two states follows a Poisson process as

$$P ( t _ { i j } > t ) = e ^ { - \lambda _ { i j } t } , \quad i , j = 1 , 2 , i \neq j ,$$

with $\lambda _ { i j }$ and $t _ { i j }$ being the transition rate from State $i$ to $j$ and the time spent in State $i$ before transferring to State $j$, respectively. $\lambda _ { X _ { t } }$ can be determined through $\lambda _ { X _ { t } } = < \bar { \lambda } , X _ { t } >$, with $\bar { \lambda }$ and $< \cdot , \cdot >$ representing the vector, $( \lambda _ { 1 } , \lambda _ { 2 } ) ^ { T }$, constructed by both state values and the inner product of two vectors, respectively. Clearly, when $\lambda _ { 1 } = \lambda _ { 2 } = 0$, our new stochastic volatility model will degenerate to the well-known Heston model.

It should be remarked that as a result of introducing another diffusion term, the feller condition that guarantees the positivity of the volatility under the Heston model breaks down, and our model is unable to prevent the volatility from going negative. However, one should not devalue our model, as the Feller condition for the Heston model is actually difficult to achieve in practice and often violated with real market data (Clark 2011). Moreover, sometimes one needs to sacrifice some basic properties in order to achieve the analytical tractability and better data fitness, typical examples of which include the well-known Stein-Stein model (Stein and Stein 1991; Grzelak et al. 2012) and the rough Heston model (El Euch and Rosenbaum 2019, 2018).

It also needs to be pointed out that the aim of this paper is to introduce regime switching into the volatility of volatility while at the same time preserving analytical tractability. In order to achieve this, a new diffusion term is incorporated into the Heston model, and one can easily observe that the volatility of volatility under our newly proposed model is controlled by two components. The first part is associated with the volatility value itself, while the second part $\lambda _ { X _ { t } }$ is governed by the Markov chain. In this sense, $\lambda _ { 1 }$ and $\lambda _ { 2 }$ can be regarded as the levels of the volatility of volatility associated with economic circles.

Having introduced the new dynamics for the underlying price, it is time to proceed to derive the closed-form pricing formula for European options under this model, which is discussed in the next subsection.

## 2.2 Valuation of European Options

In this subsection, European options are analytically priced under the newly proposed model. In particular, if the underlying price $S _ { t }$ is assumed to follow the dynamics (2.1) and (2.2), the European call option price $U ( S , \nu , X _ { t } , t )$ can be calculated as

S. Lin, X.-J. He

$$\begin{array}{l} U(S, v, X_{t}, t) = e^{-r(T-t)} E[(S_{T} - K)^{+} | S_{t}], \\ \quad = e^{-r\tau} \int_{\ln(K)}^{+\infty} (e^{y} - K) p(y) \, dy, \\ \quad = e^{-r\tau} \int_{\ln(K)}^{+\infty} e^{y} p(y) \, dy - K e^{-r\tau} \int_{\ln(K)}^{+\infty} p(y) \, dy, \end{array} \tag{2.3}$$

where $y_{t} = \ln S_{t}$, and $p(y)$ is defined as the probability density function of $y_{T}$. Obviously, if we can work out this probability density function, it is very straightforward to obtain the objective option price. However, it is usually very difficult to find the density function of the underlying price, and thus we have to find alternative ways. In fact, according to the Gil-Pelaez theorem (Wendel 1961; Shephard 1991), we can further derive

$$\int_{\ln(K)}^{+\infty} p(y) \, dy = \frac{1}{2} + \frac{1}{\pi} \int_{0}^{+\infty} RE \left[ \frac{e^{-j\phi \ln K}}{j\phi} m(\phi) \right] d\phi \triangleq P_{2}, \tag{2.4}$$

with $j$ being the imaginary unit and $m(\phi; t, y_{t}, v_{t}, X_{t})$ being the characteristic function of $y_{T}$. Moreover, if one uses the following property of the characteristic function

$$\int_{-\infty}^{+\infty} e^{y} p(y) \, dy = m(-j; t, y_{t}, v_{t}, X_{t}), \tag{2.5}$$

it is not difficult to find that $\frac{e^{y} p(y)}{m(-j; t, y_{t}, v_{t}, X_{t})}$ is the density function of another random variable. Thus, another unknown integral in the expression (2.3) can be calculated through

$$\begin{array}{l} \int_{\ln(K)}^{+\infty} e^{y} p(y) \, dy = m(-j; t, y_{t}, v_{t}, X_{t}) \left\{ \frac{1}{2} + \frac{1}{\pi} \int_{0}^{+\infty} RE \left[ \frac{e^{-j\phi \ln K}}{j\phi} \bar{m}(\phi) \right] d\phi \right\} \\ \quad \triangleq m(-j; t, y_{t}, v_{t}, X_{t}) P_{1}, \end{array} \tag{2.6}$$

where $\bar{m}(\phi; t, y_{t}, v_{t}, X_{t})$ is the characteristic function of this particular random variable defined as

$$\bar{m}(\phi; t, y_{t}, v_{t}, X_{t}) = \frac{m(\phi - j; t, y_{t}, v_{t}, X_{t})}{m(-j; t, y_{t}, v_{t}, X_{t})}. \tag{2.7}$$

Therefore, the European option price can be arranged as

$$U(S, v, X_{t}, t) = e^{-r(T-t)} [m(-j; t, y_{t}, v_{t}, X_{t}) P_{1} - K P_{2}]. \tag{2.8}$$

Clearly, we can finally obtain the European call option price if we have found the analytical formula for the characteristic function, which is what we would focus on in the following.

It should be noted that there are mainly two approaches when dealing with regime switching models. The first category tries to directly derive value functions corresponding to different regimes by establishing a coupled PDE (partial

Analytically Pricing European Options under a New...

differential equation) system (Dai et al. 2010; Tsekrekos and Yannacopoulos 2016). On the other hand, the second category is a two-step solution procedure, which separates the Markov chain from other random variables (Elliott et al. 2007; Elliott and Lian 2013; He and Zhu 2019). As it is a real challenge to directly figure out the characteristic function, we follow the approach in the second category to divide the solution process into two steps. In particular, according to the tower rule of expectation, we can obtain

$$m(\phi; t, y_t, v_t, X_t) = E[e^{j\phi y_T} | y_t, v_t, X_t] \tag{2.9}$$

$$= E\{E[e^{j\phi y_T} | y_t, v_t, X_T] | X_t\}.$$

One can see clearly here that the second approach tries to first work out the inner expectation, in which the information of the Markov chain is given, and the second step is to focus on the outer expectation with respect to the Markov chain only. If we further define the inner expectation of Eq. (2.9) as the conditional characteristic function $h(\phi; t, y_t, v_t | X_T)$ (denoted by $h(\phi | X_T)$ in the following)

$$h(\phi | X_T) = E[e^{j\phi y_T} | y_t, v_t, X_T], \tag{2.10}$$

it is not difficult to find that when deriving $h(\phi | X_T)$, $\lambda_{X_t}$ is no longer a parameter that would randomly change with the Markov chain, but rather a deterministic function of the time, i.e., $\lambda_t$, which means that no coupled PDE system will be established here. Therefore, the PDE system governing $h(\phi | X_T)$ can be easily found according to the Feynman–Kac theorem

$$\left\{ \begin{array}{l} \frac{\partial h}{\partial t} + \frac{1}{2}v \frac{\partial^2 h}{\partial y^2} + \frac{1}{2}(\sigma^2 v + \lambda_t^2) \frac{\partial^2 h}{\partial v^2} + \rho \sigma v \frac{\partial^2 h}{\partial v \partial y} \\ \quad + \left(r - \frac{1}{2}v\right) \frac{\partial h}{\partial y} + k(\theta - v) \frac{\partial h}{\partial v} = 0, \\ \quad h(\phi; t, v_t, X_t)|_{t=T} = e^{j\phi y_T}. \end{array} \right. \tag{2.11}$$

Following Heston (1993), we assume that $h(\phi | X_T)$ takes the form of

$$h(\phi | X_T) = e^{C(\phi; \tau) + D(\phi; \tau)v + j\phi y}, \tag{2.12}$$

with $\tau = T - t$, and then substituting it into the PDE contained in system (2.11) yields two ODEs (ordinary differential equations)

$$\frac{\partial D}{\partial \tau} = \frac{1}{2}\sigma^2 D^2 + (j\phi\rho\sigma - k)D - \frac{1}{2}(j\phi + \phi^2), \tag{2.13}$$

$$\frac{\partial C}{\partial \tau} = \frac{1}{2}\lambda_t^2 D^2 + k\theta D + rj\phi.$$

Obviously, the ODE governing $D(\phi; \tau)$ is a Riccati equation with constant coefficients, and it can be transformed into a second order linear ODE for $Z$ with the

S. Lin, X.-J. He

transformation of $Z = \frac{2 \frac{dD}{d\tau}}{\sigma^2 D}$, which can be easily solved with some simple algebraic calculations. As a result, the expression of $D(\phi; \tau)$ can be derived as

$$D = \frac{d - (j\phi\rho\sigma - k)}{\sigma^2} \frac{1 - e^{d\tau}}{1 - g e^{d\tau}}, \tag{2.14}$$

where

$$d = \sqrt{(j\phi\rho\sigma - k)^2 + \sigma^2(j\phi + \phi^2)}, g = \frac{(j\phi\rho\sigma - k) - d}{(j\phi\rho\sigma - k) + d}.$$

With the analytical formula for $D(\phi; \tau)$ being derived, we can straightforwardly obtain the formula of $C(\phi; \tau)$ by directly integrating on both sides of the governing ODE, which gives

$$C = rj\phi\tau + \frac{k\theta}{\sigma^2} \{[d - (j\phi\rho\sigma - k)]\tau - 2\ln[\frac{1 - g e^{d\tau}}{1 - g}]\} + \frac{1}{2} \int_t^T <\lambda_s^2 D^2(\phi; T - s), X_s > ds. \tag{2.15}$$

By now, we have already obtained the conditional characteristic function of the underlying price, and thus the target characteristic function, which is also the outer expectation contained in Equation (2.9), can be calculated as

$$\begin{aligned} m(\phi; t, y_t, v_t, X_t) &= E[h(\phi|X_T)|X_t] \\ &= e^{\bar{C} + Dv + i\phi y} E[e^{\frac{1}{2}\int_t^T <\lambda_s^2 D^2(\phi; T-s), X_s > ds}|X_t], \tag{2.16} \end{aligned}$$

where $\bar{C} = rj\phi\tau + \frac{k\theta}{\sigma^2} \{[d - (j\phi\rho\sigma - k)]\tau - 2\ln[\frac{1 - g e^{d\tau}}{1 - g}]\}$. From this, it is not difficult to find that the left work is to figure out the expectation in the above equation before we can obtain the expression of the characteristic function. In fact, according to the results in Elliott and Lian (2013), this particular expression can be further derived as

$$E[e^{\frac{1}{2}\int_t^T <\lambda_s^2 D^2(\phi; T-s), X_s > ds}|X_t] = <e^M X_t, I>, \tag{2.17}$$

where $X_t \in \{(1, 0)^T, (0, 1)^T\}$, and $I = (1, 1)^T$. The matrix $M$ is

$$M = \int_t^T A^T + diag[\frac{1}{2}\lambda_{X_t}^2 D^2(\phi; T - s)] ds, \tag{2.18}$$

with $A$ being the transition rate matrix

$$A = \begin{pmatrix} -\lambda_{12} & \lambda_{12} \\ \lambda_{21} & -\lambda_{21} \end{pmatrix}.$$

Working out the integration in the expression of $M$ leads to the analytical formula of $M$ as

Analytically Pricing European Options under a New...

$$M = \left( \begin{array}{cc} -\lambda_{12}\tau + \frac{1}{2}\lambda_1^2 f(\phi; \tau) & \lambda_{21}\tau \\ \lambda_{12}\tau & -\lambda_{21} + \frac{1}{2}\lambda_2^2 f(\phi; \tau) \end{array} \right).$$

Here, $f(\phi; \tau)$ is defined as

$$f(\phi; \tau) = \frac{1}{\sigma^4} \left\{ [d - (j\phi\rho\sigma - k)]^2 \tau + 4(j\phi\rho\sigma - k) \ln \left[ \frac{1 - ge^{d\tau}}{1 - g} \right] + \frac{4d}{1 - ge^{d\tau}} - \frac{4d}{1 - g} \right\}. \tag{2.19}$$

Hence, we have finally arrived at the desired characteristic function

$$m(\phi; t, y_t, v_t, X_t) = e^{\bar{C} + Dv + i\phi y} < e^M X_t, I >. \tag{2.20}$$

With the pricing formula (2.8) and the characteristic function (2.20), we can now confidently draw the conclusion that we have derived the closed-form pricing formula under the newly proposed stochastic volatility model with regime switching. However, to ensure that there are no algebraic errors involved in the derivation process, numerical experiments still need to be conducted to verify the accuracy of the formula. It is also interesting to show the difference between our model and the well-known Heston model to investigate the influence of introducing regime switching. These two issues are presented in the next section.

### 3 Numerical Experiments and Examples

In this section, we will firstly verify our pricing formula by comparing European option prices calculated with our formula and those obtained through the Monte Carlo simulation to ensure there are no algebraic errors. After this, the difference between our model and the Heston model will be shown through the comparison of option prices under our model and the Heston model. Unless otherwise stated, the values of the parameters we use to generate the figures in this section are listed as follows. The mean reversion speed and level, $k$ and $\theta$, take the value of 10 and 0.08, respectively, and the constant volatility of volatility $\sigma$ is allocated as 0.1. The correlation $\rho$ between the underlying price and the volatility is set to be -0.5, while the risk free interest rate $r$ is chosen as 0.05. The two transition rates of the Markov chain, $\lambda_{12}$ and $\lambda_{21}$, are assumed to be 10 and 20 respectively, and the strike price $K$ defaults as 10. The current value of the volatility $v_0$ is 0.03, and the current state of the regime switching is assumed to be 1.

In order to ensure the accuracy of the newly derived formula for European call options, prices obtained with our formula are compared with those Monte Carlo prices. As the traditional Monte Carlo simulation technique takes a large amount of time when dealing with stochastic processes containing regime switching, we adopt a semi-Monte-Carlo simulation (Liu et al. 2006) to improve the efficiency of Monte Carlo simulation. Specifically, as the traditional Monte Carlo simulation, we still generate 500,000 paths with each path resulting one option price and take the

7

S. Lin, X.-J. He

average of these prices to obtain one Monte Carlo price. However, in each path, instead of generating all the random variables, we only generate the Markov chain $X_t$ with time $t \in [0, T]$ so that $\lambda_{X_t}$ becomes a time-dependent parameter. In this case, European option prices corresponding to this path can be calculated through the formula (2.8) with the characteristic function replaced by the conditional characteristic function since all the information of the Markov chain is known. With this particular semi-Monte-Carlo simulation, the results of comparison are shown in Fig. 1. What should be noticed first in Fig. 1a is that our prices are a monotonic increasing function of the underlying price, which is consistent with financial intuition. Moreover, our prices agree very well with Monte Carlo prices under the same set of parameters, confirming the accuracy of this formula. This is further demonstrated with the maximum relative error between the two prices being no greater than 0.7%, as presented in Fig. 1b.

From the model specification, it is not difficult to find that the well-known Heston model is a special case of our newly proposed model if $\lambda_1 = \lambda_2 = 0$, which implies that our formula should also be able to degenerate to the Heston formula under this particular choice of parameters. In order to show this property, we introduce a scale parameter $z$ varying within the range $[0, 1]$ so that the value of $\lambda_1$ and $\lambda_2$ will change with $z$, by making it a common factor of the two parameters. In this case, European option prices under our model and the Heston model are depicted in Fig. 2 with respect to the value of $z$. It is clear that our price is no larger than the Heston price under the chosen parameters, and the distance between the two prices are widened when we enlarge the value of $\lambda_1$ and $\lambda_2$. Moreover, one can clearly find that our price becomes exactly the same as the Heston price when $\lambda_1$ and $\lambda_2$ are set to be zero, which is expected since the part of the volatility of volatility controlled by the Markov chain can be regarded as removed in this case.

To see how differently our model behaves from the Heston model with all the corresponding parameters being the same, European call option prices under the two models with respect to time to expiry are presented in Fig. 3. A common feature for the two models is that option prices are an increasing function of the time to expiry, which is reasonable since there would be more chance for the underlying price to

![img-0.jpeg](img-0.jpeg)

(a) Our price vs Monte Carlo price.

![img-1.jpeg](img-1.jpeg)

(b) Relative error between our price and Monte Carlo price.

Fig. 1 The comparison of variance swap prices from our formula and Monte Carlo simulation. Parameters are $T = 0.5, \lambda_1 = 0.01; \lambda_2 = 0.05$.

Analytically Pricing European Options under a New...

![img-2.jpeg](img-2.jpeg)

Fig. 2 European option prices under our model and the Heston model with the scale parameter z. Model parameters are T = 0.5; S = 10; λ₁ = 0.3 * z; λ₂ = 0.2 * z.

![img-3.jpeg](img-3.jpeg)

Fig. 3 European option prices under our model and the Heston model with the time to maturity. Model parameters are S = 10; λ₁ = 0.3; λ₂ = 0.2

reach a higher level if the time to maturity becomes longer. Moreover, it should be noted that although option prices under the Heston model is always higher than those under our newly proposed model with the chosen parameters, one should never draw the conclusion that there would always exist such a relationship between the Heston model and our model when the corresponding parameters are set to be different under the two models, which is usually the case when both models are

S. Lin, X.-J. He

calibrated with real market data. It is also interesting to find that with the time to maturity being larger, the difference between the two prices is narrowed down.

It should be remarked that Fig. 1 has already shown how option prices evolve with respect to the underlying price, and that is why the underlying price is set to be the same in Figs. 2 and 3, when we investigate the influence of other parameters on option prices. Also, we use different values of $\lambda_1$ and $\lambda_2$ in Figs. 2 and 3 simply because Fig. 2 tries to identify the effect of $\lambda_1$ and $\lambda_2$ so we have to vary their values, while Fig. 3 focuses on the impact of another variable, the time to expiry, in which case there is no need for us to change values of other parameters. Of course, the pricing difference between our model and the Heston model using artificial data does not necessarily imply that our model is able to provide better performance, when real market data is employed, and whether it is meaningful to introduce the second factor in the volatility process remains to be investigated, which is the main topic of the next section.

## 4 Empirical Studies

In this section, an empirical study is carried out, with the Heston model used to benchmark the performance of our model, to show the importance of introducing a second regime switching factor into the Heston model. The Elliott–Lian model (Elliott and Lian 2013) is also calibrated with the same set of data to further justify our approach of introducing regime switching. This section is further divided into three subsections, introducing the data set used along with several appropriate filters, describing the approach for parameter estimation, and presenting empirical results, respectively.

### 4.1 Data Description

European call options written on the S&P 500 Index ranging from Jan 2011 to June 2011 are adopted for the calibration of the three models. Before we determine model parameters, several filters need to be applied to eliminate sample noise, so that possible mis-leading conclusions can be avoided.

First of all, as Wednesday is least likely to be holidays in a week and less likely to be affected by the “day-of-the-week” effect (Bakshi et al. 1997; Christoffersen et al. 2006), only Wednesday options data are selected for estimating model parameters, the practice of which also allows us to study a relatively long period, due to the time-intensiveness of the model calibration process. Moreover, options with less than 30 days or more than 90 days to expiry are removed, since options with small/large time to expiry usually have liquidity problems due to their volatile/high trading premium (Le 2015). Finally, options with the absolute moneyness being higher than 10%, i.e., $|\frac{S - K}{K}| \geq 10\%$, are discarded as well due to their unpopularity in real markets (Shu and Zhang 2004).

In addition to these filters, the risk-free interest rate should also be determined, and following (Benjamin et al. 2007; Shu and Zhang 2004), the three-month daily

Springer

Analytically Pricing European Options under a New...

U.S. Treasury Bill Rate is chosen as its proxy. Having finished all these prior steps, parameters can be determined from the filtered data set, the details of which are to be illustrated in the next subsection.

## 4.2 Parameter Estimation

The first step in the stage of parameter estimation is always to distinguish parameters that need to be determined from those available once the option contract is entered. Thus, it is necessary for us to clarify the parameters under three models that need to be extracted from market data. In particular, the Heston model contains five model parameters, including the mean reversion speed k, mean reversion level θ, volatility of volatility σ, initial level of volatility ν₀, and the correlation ρ. On the other hand, after introducing regime switching, four additional parameters are included in our model, i.e., the two state values of the regime switching volatility of volatility, λ₁, λ₂, and two transition rates, λ₁₂, λ₂₁, while the Elliott–Lian model³ replaces θ in the Heston model with two state values for the mean reversion level θ₁ and θ₂, accompanied by the same two transition rates.

Clearly, all we need to do now is to determine these model parameters through a model calibration process, which essentially searches for the “best” set of parameters such that for a particular chosen option data set, the produced model prices are “closet” to their listed market prices. This is usually achieved by formulating the model calibration as a minimization problem, where we try to minimize the “distance” between the market and model prices. In view of this and following a number of different authors (Christoffersen and Jacobs 2004; Lim and Zhi 2002), our problem is transformed into minimizing the following dollar mean-squared error (MSE)

$$MSE = \frac{1}{N} \sum_{i=1}^{N} [C_i^{Market} - C_i^{Model}]^2, \tag{4.1}$$

where N is the total number of observations selected in a single estimation, and Cᵢ^Market and Cᵢ^Model represent the market price⁴ of the i-th option and the price of the same option calculated with our formula, respectively.

To realize this, a good optimization technique is vital, which can mainly be classified into two categories, i.e., local and global optimization. The former category, though being easy and fast to implement, is not appropriate for our purpose here, since our objective function (4.1) is not necessarily convex and thus there exist several local minima, which could probably result in the algorithm ending up with a local minimum. The latter one, on the other hand, is designed to avoid being stuck in local minima to ensure that the global minimum is attainable, and is thus much preferred in most of model calibration processes.

³ The Elliott–Lian model (Elliott and Lian 2013) is constructed by incorporating a regime switching mean reversion level into the Heston model, so that the volatility process becomes dvₜ = k(θₓᵢ - νₜ)dt + σ√νₜdWₜ².

⁴ As there exist two prices, the so-called bid and ask prices, for an option in real markets, we follow the common practice to use the average of bid and ask prices as the market price.

S. Lin, X.-J. He

The simulated annealing (SA) (Kirkpatrick et al. 1983) is one of the best known global optimization techniques, as in addition to its advantages of being easy to program and having few parameters that require tuning, it is also equipped with the theoretical guarantee of the convergence of the algorithm. However, its slow speed of convergence hinders its potential practical applications, and this has prompted the development of various modifications, among which the adaptive simulated annealing (ASA) is a well-known variation (Ingber 1989). It is particularly designed to find the best global fit of a non-linear constrained non-convex cost function over a D-dimensional space (Ingber et al. 2012), and is much more efficient and less sensitive to user defined parameters than the SA does, in addition to preserving all the advantages of the SA. The ASA has had wide applications in different areas, and has already been applied in the calibration of option pricing models (Poklewski-Koziell 2013; Mikhailov and Nögel 2003).

As a result, the ASA is adopted here to determine parameters for all the three models, and it is implemented through the open-source code provided in Ingber (2018), the availability of which enables it to be assessed by different users, making it possible to be more flexible and powerful. The estimated daily-averaged results are reported in Table 1.

With the model parameters being successfully determined from the chosen data set, we are now able to compare the performance of the three models, the details of which are to be discussed in the next subsection.

### 4.3 Empirical Results

The two types of errors, in- and out-of-sample errors, play an important role in assessing model performance. In particular, in-sample errors are referred to as the remaining errors between market and model prices of the data set used for estimation (Wednesday data), while out-of-sample errors are obtained by calculating the difference between market and model prices of a different data set that has not been used for estimating parameters (Thursday data is used for this purpose). Table 2 below summarizes the in- and out-of-sample errors of the three models.

Clearly, a simple comparison of in- and out-of-sample errors exhibited by the three models in Table 2 indicates that our newly proposed model greatly outperforms the Heston model without regime switching as well as the Elliott-Lian model with a regime switching mean reversion level. On one hand, the daily averaged in-sample MSE provided by our model is 0.0480, which is slightly more than 50% of that produced by the Heston model, and it is also around 30% less than that of the Elliott-Lian model. On the other hand, our model also shows 30 and 20% improvement in the out-of-sample errors, compared with that of the Heston model and that of the Elliott-Lian model, respectively. It can be inferred from these phenomenons that our approach for the introduction of regime switching can result in the improvement in the data fitness, which is also a clear evidence that our model serves as a better choice than both the Heston model and the Elliott-Lian model, at least for this particular data set.

It is also of practical interest to see the model performance across different moneyness, and thus Table 3 is produced to display the out-of-sample errors for out-

Table 1 Estimated parameters

|  Parameters | Our model | Elliott-Lian model | Heston model  |
| --- | --- | --- | --- |
|  k | 8.4168 | 7.6130 | 8.7384  |
|  θ(θ₁) | 0.1986 | 0.1002 | 0.0817  |
|  θ₂ |  | 0.1544 |   |
|  σ | 0.7503 | 1.0089 | 1.4136  |
|  λ₁ | 0.0453 |  |   |
|  λ₂ | 0.0360 |  |   |
|  ρ | -0.6293 | -0.3621 | -0.3089  |
|  ν₀ | 0.0249 | 0.0253 | 0.0260  |
|  λ₁₂ | 12.1224 | 9.2372 |   |
|  λ₂₁ | 4.9125 | 6.0937 |   |

Table 2 In- and out-of-sample errors for the two models

|  Error | In-sample | Out-of-sample  |
| --- | --- | --- |
|  Our model | 0.0480 | 2.3186  |
|  Elliott-Lian model | 0.0688 | 2.8825  |
|  Heston model | 0.0879 | 3.2981  |

Table 3 Out-of-sample errors according to moneyness

|  Moneyness | Out-of-money | At-the-money | In-the-money  |
| --- | --- | --- | --- |
|  Our model | 0.7316 | 5.1446 | 2.0252  |
|  Elliott-Lian model | 6.6006 | 7.5843 | 2.0315  |
|  Heston model | 2.7015 | 10.3103 | 2.0513  |

of-money, at-the-money and in-the-money options, which are respectively defined when 0.90<S/K<0.97, 0.97≤S/K≤1.03 and 1.03<S/K<1.10. One can certainly observe from this table that our model performs better than both the Heston model and the Elliott-Lian model for all the three categories, though the performance of the three models is very similar when in-the-money options are taken into consideration. The greatest improvement occurs in the out-of-money options, with the MSE of our model being only around a quarter of that from the Heston model, and within this category the Elliott-Lian model performs even much worse than the Heston model. Our model also shows significantly improved performance for at-the-money options, with our MSE being only half and two thirds of that from the Heston model and the Elliott-Lian model, respectively.

## 5 Conclusion

In this paper, we propose a two-factor stochastic volatility model for the pricing of European options. This model is advantageous not only because it is able to capture the effect of regime switching in the volatility process, it also possesses a closed-

form pricing formula, which ensures the computational efficiency in option pricing and model calibration. The results of our empirical study further demonstrate the advantages of our model, as our model is shown to generally outperform the Heston model and the Elliott–Lian model for the selected data set, implying that our model can at least act as a good competitor to these two models in practice. Of course, it is interesting to investigate how option prices would evolve if other parameters are also regime switching. However, this will definitely bring extra difficulty in finding the analytical pricing formula and will be left for future research.

Acknowledgements The authors would like to gratefully acknowledge anonymous referees' constructive comments and suggestions, which greatly help to improve the readability of the manuscript.

References

Abhishekh, Bharati, S. K., & Singh, S. R. (2019). A novel approach to handling forecasting problems based on moving average two-factor fuzzy time series. Advances in Intelligent Systems and Computing, 816, 295–309.
Abhishekh, & Kumar, S., (2019). A modified weighted fuzzy time series model for forecasting based on two factors logical relationship. International Journal of Fuzzy Systems, 21(5), 1403–1417.
Bakshi, G., Cao, C., & Chen, Z. (1997). Empirical performance of alternative option pricing models. The Journal of Finance, 52(5), 2003–2049.
Benjamin, M. A., Hinnant, H. O., Shigeno, T. T., & Olmstead, D. N. (2007). Multi-sensor fusion, Oct. 16. U.S. Patent 7,283,904.
Black, F., & Scholes, M. (1973). The pricing of options and corporate liabilities. The Journal of Political Economy, 81(3), 637–654.
Christoffersen, P., Heston, S., & Jacobs, K. (2009). The shape and term structure of the index option smirk: Why multifactor stochastic volatility models work so well. Management Science, 55(12), 1914–1932.
Christoffersen, P., & Jacobs, K. (2004). Which GARCH model for option valuation? Management Science, 50(9), 1204–1221.
Christoffersen, P., Jacobs, K., & Mimouni, K. (2006). An empirical comparison of affine and non-affine models for equity index options. Springer.
Clark, I. J. (2011). Foreign exchange option pricing: A practitioner's guide. Wiley.
Dai, M., Zhang, Q., & Zhu, Q. J. (2010). Trend following trading under a regime switching model. SIMA Journal on Financial Mathematics, 1(1), 780–810.
Dumas, B., Fleming, J., & Whaley, R. E. (1998). Implied volatility functions: Empirical tests. The Journal of Finance, 53(6), 2059–2106.
Dupire, B., et al. (1994). Pricing with a smile. Risk, 7(1), 18–20.
El Euch, O., & Rosenbaum, M. (2018). Perfect hedging in rough Heston models. The Annals of Applied Probability, 28(6), 3813–3856.
El Euch, O., & Rosenbaum, M. (2019). The characteristic function of rough Heston models. Mathematical Finance, 29(1), 3–38.
Elliott, R. J., Kuen Siu, T., & Chan, L. (2007). Pricing volatility swaps under Heston's stochastic volatility model with regime switching. Applied Mathematical Finance, 14(1), 41–62.
Elliott, R. J., & Lian, G.-H. (2013). Pricing variance and volatility swaps in a stochastic volatility model with regime switching: Discrete observations case. Quantitative Finance, 13(5), 687–698.
Grzelak, L. A., Oosterlee, C. W., & VanWeeren, S. (2012). Extension of stochastic volatility equity models with the Hull–White interest rate process. Quantitative Finance, 12(1), 89–105.
Hagan, P. S., Kumar, D., Lesniewski, A. S., & Woodward, D. E. (2002). Managing smile risk. The Best of Wilmott, 1, 249–296.
He, X.-J., & Zhu, S.-P. (2016). An analytical approximation formula for European option pricing under a new stochastic volatility model with regime-switching. Journal of Economic Dynamics and Control, 71, 77–85.

Analytically Pricing European Options under a New...

He, X.-J., & Zhu, S.-P. (2019). Variance and volatility swaps under a two-factor stochastic volatility model with regime switching. International Journal of Theoretical and Applied Finance, 22(4), 1950009.

Heston, S. L. (1993). A closed-form solution for options with stochastic volatility with applications to bond and currency options. Review of Financial Studies, 6(2), 327–343.

Hull, J., & White, A. (1987). The pricing of options on assets with stochastic volatilities. The Journal of Finance, 42(2), 281–300.

Ingber, L. (1989). Very fast simulated re-annealing. Mathematical and Computer Modelling, 12(8), 967–973.

Ingber, L. (2018). Home page of lester ingber. https://www.ingber.com.
Ingber, L., Petraglia, A., Petraglia, M. R., & Machado, M. A. S. et al. (2012). Adaptive simulated annealing. In Stochastic global optimization and its applications with fuzzy adaptive simulated annealing (pp. 33–62). Springer.

Jacquier, E., Polson, N. G., & Rossi, P. E. (2004). Bayesian analysis of stochastic volatility models with fat-tails and correlated errors. Journal of Econometrics, 122(1), 185–212.

Kaeck, A., & Alexander, C. (2010). VIX dynamics with stochastic volatility of volatility. ICMA Centre, Henley Business School, University of Reading.

Kalimipalli, M., & Susmel, R. (2004). Regime-switching stochastic volatility and short-term interest rates. Journal of Empirical Finance, 11(3), 309–329.

Kamp, R. (2009). Local volatility modelling. Master’s thesis, University of Twente.
Kirkpatrick, S., Gelatt, C. D., Vecchi, M. P., et al. (1983). Optimization by simulated annealing. Science, 220(4598), 671–680.

Le, A. (2015). Separating the components of default risk: A derivative-based approach. The Quarterly Journal of Finance, 5(01), 1550005.

Lim, K. G., & Zhi, D. (2002). Pricing options using implied trees: Evidence from FTSE-100 options. Journal of Futures Markets, 22(7), 601–626.

Liu, R., Zhang, Q., & Yin, G. (2006). Option pricing in a regime-switching model using the fast Fourier transform. International Journal of Stochastic Analysis, 2006, 1–22.

Mikhailov, S., & Nögel, U. (2003). Heston’s stochastic volatility model: Implementation, calibration and some extensions. Wilmott Magazine, 2003, 74–79.

Pacati, C., Pompa, G., & Renò, R. (2018). Smiling twice: The Heston++ model. Journal of Banking & Finance, 96, 185–206.

Pacati, C., Renò, R., & Santilli, M. (2014). Heston model: Shifting on the volatility surface. Risk, 2014, 54–59.

Poklewski-Koziell, W. (2013). Stochastic volatility models: Calibration, pricing and hedging. Ph.D thesis. Doctoral dissertation, University of the Witwatersrand.

Scott, L. O. (1987). Option pricing when the variance changes randomly: Theory, estimation, and an application. Journal of Financial and Quantitative analysis, 22(04), 419–438.

Shephard, N. G. (1991). From characteristic function to distribution function: A simple framework for the theory. Econometric Theory, 7, 519–529.

Shu, J., & Zhang, J. E. (2004). Pricing S&P 500 index options under stochastic volatility with the indirect inference method. Journal of Derivatives Accounting, 1(2), 1–16.

Stein, E. M., & Stein, J. C. (1991). Stock price distributions with stochastic volatility: An analytic approach. Review of Financial Studies, 4(4), 727–752.

Tsekrekos, A. E., & Yannacopoulos, A. N. (2016). Optimal switching decisions under stochastic volatility with fast mean reversion. European Journal of Operational Research, 251(1), 148–157.

Vo, M. T. (2009). Regime-switching stochastic volatility: Evidence from the crude oil market. Energy Economics, 31(5), 779–788.

Wendel, J. G. (1961). The non-absolute convergence of Gil–Pelaez’ inversion integral. The Annals of Mathematical Statistics, 32(1), 338–339.

Wiggins, J. B. (1987). Option values under stochastic volatility: Theory and empirical estimates. Journal of Financial Economics, 19(2), 351–372.

Publisher’s Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.


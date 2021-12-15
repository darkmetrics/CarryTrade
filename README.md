
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pandas?color=brightgreen&logo=Python&logoColor=yellow)

# **Article replication for International Finance course.**

Article replicated: *Can implied volatility predict returns on the currency carry trade? Egbers T., Swinkels L., Journal of Banking & Finance, 2015.*

Replication authors: Lozovoy Vladimir, Kusliaikin Aleksandr, Byzov Aleksei.

Project contains:

- folder ``data`` with datasets used in code:
   * ``Data_bloomberg.xlsx`` - the data in format it was downloaded from Bloomberg Terminal.
   * ``clean_data.xlsx`` - cleaned data from Bloomberg to preprocess further.
   * ``fx.csv`` - final version of data on FX spot and forward rates to use when testing strategies from paper. This data was obtained through preprocessing of ``clean_data.xlsx`` in Jupyter Notebook ``carry_trade.ipynb`` (see Notebook).
   * ``vol.csv`` - final version of data on VIX and VXY volatility indexes to use when testing strategies from paper. This data was obtained through preprocessing of ``clean_data.xlsx`` in Jupyter Notebook ``carry_trade.ipynb`` (see Notebook).

- folder ``images`` with high-resolution pictures generated inside our code.
- Jupyter Notebook ``carry_trade.ipynb`` with data preprocessing and article replication.
- Unnecessary file with code ``trash.py``.

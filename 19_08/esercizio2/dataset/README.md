# Global GDP and CO₂ Emissions Dataset (1960–2022)

This dataset combines GDP and CO₂ emissions data at the country level for longitudinal and comparative analysis. It merges economic and environmental indicators to support research into sustainability, development trajectories, and global inequality.

## What's Included

This dataset provides harmonized annual records for over 180 countries and territories. It includes core economic and emissions indicators, derived metrics, and regional metadata for filtering or grouping.

### File Structure

- `gdp_co2_by_country.csv`: Final cleaned dataset
- `data_descriptions.txt`: Column dictionary and notes

## Columns

| Column Name         | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| Country Name        | Official country name                                                       |
| Country Code        | ISO 3-letter country code                                                   |
| Year                | Calendar year                                                               |
| Population          | Total population                                                            |
| Pop Log             | Log-transformed population                                                  |
| Pop Outliers        | Outlier flag for population (z-score)                                       |
| Pop Category        | Population size category (e.g., low, medium, high)                          |
| CO2                 | Annual CO₂ emissions (metric tons)                                          |
| CO2 %               | Year-on-year % change in CO₂ emissions                                      |
| Per Capita CO2      | CO₂ emissions per capita                                                    |
| Cumulative CO2      | Cumulative CO₂ emissions up to that year                                    |
| CO2 Log             | Log-transformed CO₂ emissions                                               |
| CO2 Outliers        | Outlier flag for CO₂ emissions (z-score)                                    |
| Emissions Category  | Emissions band/category (e.g., low, medium, high)                           |
| GDP USD             | GDP (constant USD)                                                          |
| GDP USD Log         | Log-transformed GDP                                                         |
| GDP %               | Annual GDP growth rate (%)                                                  |
| GDP % Winsor        | Winsorized GDP growth rate (outlier handling)                               |
| GDP Per Capita      | GDP per capita (constant USD)                                               |
| GDP Category        | GDP size category (Low, Middle, High)                                       |
| CO2 Per GDP         | CO₂ emissions per unit of GDP (emissions efficiency metric)                 |

Notes:

- All monetary values are in constant USD for comparability.
- Log and winsorized columns are included to support robust statistical analysis.
- Outlier columns are based on z-score thresholds.
- Categories are based on quantiles or World Bank definitions.
- The dataset is suitable for time series, cross-sectional, and panel analysis.


## Data Sources

- CO₂ emissions: [Our World in Data](https://github.com/owid/co2-data)  
- GDP and population: [World Bank Open Data](https://data.worldbank.org/)  
- Region and income metadata: World Bank classifications

## Suggested Uses

- Emissions-growth comparison across income groups  
- Longitudinal sustainability trends  
- Climate policy dashboards and teaching tools  
- Inequality analysis based on emissions per capita

## License

MIT License. You are welcome to use, modify, and share with attribution.

## Maintainer

Katlyn Goeujon-Mackness  
GitHub: [katiemackness](https://github.com/katiemackness)  
LinkedIn: [Katlyn Goeujon-Mackness](https://www.linkedin.com/in/katlyngm-datos/)
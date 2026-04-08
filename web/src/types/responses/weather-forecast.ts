export type SkyCondition = "clear" | "cloudy" | "rain" | "snow";

export interface Forecast {
    date: string;
    dayOfWeek: string;
    dayOfWeekKo: string;
    minTemperature: number;
    maxTemperature: number;
    precipitationProbability: number;
    skyCondition: SkyCondition;
}

export interface WeatherForecastResponse {
    courseId: number;
    forecasts: Forecast[];
}

import React, { useEffect, useState } from "react";
import type { Forecast, SkyCondition, WeatherForecastResponse } from "@/types/responses/weather-forecast";
import { FORECAST_DAYS } from "@/vars/weather";

interface Props {
    courseId: number | undefined;
}

const SkyConditionIcon: React.FC<{ condition: SkyCondition }> = ({ condition }) => {
    switch (condition) {
        case "clear":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <circle cx="12" cy="12" r="4" fill="currentColor" />
                    <path strokeLinecap="round" d="M12 2v4M12 18v4M2 12h4M18 12h4M17.66 6.34l1.41-1.41M6.34 6.34l-1.41-1.41M6.34 17.66l-1.41 1.41M17.66 17.66l1.41 1.41" />
                </svg>
            );
        case "cloudy":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
                </svg>
            );
        case "rain":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
                    <path d="M8 19v3m4-3v3m4-3v3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
            );
        case "snow":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-sky-300" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
                    <circle cx="8" cy="21" r="1" /><circle cx="12" cy="21" r="1" /><circle cx="16" cy="21" r="1" />
                </svg>
            );
    }
};

const SKY_CONDITION_LABELS: Record<SkyCondition, string> = { // 한글 레이블, Record는 타입스크립트의 유틸리티 타입으로, 키와 값의 타입을 지정할 때 사용
    clear: "맑음",
    cloudy: "흐림",
    rain: "비",
    snow: "눈",
};

const isWeekend = (dayOfWeekKo: string): boolean => {
    return dayOfWeekKo === "토" || dayOfWeekKo === "일";
};

const formatDate = (dateStr: string): string => {
    const [, month, day] = dateStr.split("-");
    return `${parseInt(month)}/${parseInt(day)}`;
};

const WeatherForecast: React.FC<Props> = ({ courseId }: Props) => {
    const [forecasts, setForecasts] = useState<Forecast[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<boolean>(false);

    useEffect(() => {
        if (courseId === undefined) return;

        setLoading(true);
        fetch(`${import.meta.env.PUBLIC_API_ENDPOINT}/v1/courses/${courseId}/weather/forecast?days=${FORECAST_DAYS}`)
            .then((res) => {
                if (!res.ok) throw new Error("Failed to fetch forecast");
                return res.json();
            })
            .then((data: WeatherForecastResponse) => {
                setForecasts(data.forecasts);
            })
            .catch(() => {
                setError(true);
            })
            .finally(() => setLoading(false));
    }, [courseId]);

    if (loading) {
        return (
            <div className="my-6">
                <p className="text-sm font-bold text-base-content/60 mb-3">주간 날씨 예보</p>
                <div className="flex gap-2 overflow-x-auto">
                    {Array.from({ length: FORECAST_DAYS }).map((_, i) => (
                        <div key={i} className="skeleton h-36 w-20 shrink-0 rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    if (error || forecasts.length === 0) return null;

    return (
        <div className="my-6">
            <p className="text-sm font-bold text-base-content/60 mb-3">주간 날씨 예보</p>
            <div className="flex gap-2 overflow-x-auto pb-2">
                {forecasts.map((forecast) => {
                    const weekend = isWeekend(forecast.dayOfWeekKo);
                    return (
                        <div
                            key={forecast.date}
                            className={`flex flex-col items-center gap-1.5 px-4 py-3 rounded-lg shrink-0 flex-1 min-w-[80px] border ${
                                weekend
                                    ? "bg-red-50 border-red-200"
                                    : "bg-base-100 border-base-content/10"
                            }`}
                        >
                            {/* 요일 */}
                            <span className={`text-sm font-bold ${weekend ? "text-red-500" : ""}`}>
                                {forecast.dayOfWeekKo}
                            </span>

                            {/* 날짜 */}
                            <span className="text-xs text-base-content/50">
                                {formatDate(forecast.date)}
                            </span>

                            {/* 날씨 아이콘 */}
                            <div className="my-1" title={SKY_CONDITION_LABELS[forecast.skyCondition]}>
                                <SkyConditionIcon condition={forecast.skyCondition} />
                            </div>

                            {/* 최저/최고 온도 */}
                            <div className="text-xs font-semibold">
                                <span className="text-blue-500">{forecast.minTemperature}°</span>
                                {" / "}
                                <span className="text-red-500">{forecast.maxTemperature}°</span>
                            </div>

                            {/* 강수확률 */}
                            {forecast.precipitationProbability > 0 ? (
                                <span className={`text-xs ${
                                    forecast.precipitationProbability >= 40
                                        ? "text-blue-500 font-bold"
                                        : "text-base-content/40"
                                }`}>
                                    강수확률 {forecast.precipitationProbability}%
                                </span>
                            ) : (
                                <span className="text-xs text-base-content/20">-</span>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default WeatherForecast;

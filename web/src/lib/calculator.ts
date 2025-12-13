import type { Point } from "@/types/common/location";

export function calculateMediumPoint(points: Point[]): Point {
    if (points.length === 0) {
        throw new Error("Input array is empty");
    }

    if (points.length === 1) {
        return points[0];
    }

    // 1. 모든 점들의 위도와 경도의 평균을 계산합니다.
    const total = points.reduce(
        (acc, point) => {
            acc.lat += point.lat;
            acc.lon += point.lon;
            return acc;
        },
        { lat: 0, lon: 0 }
    );

    const center = {
        lat: total.lat / points.length,
        lon: total.lon / points.length,
    };

    // 2. 중심점에서 가장 가까운 점을 찾습니다.
    // 유클리드 거리의 제곱을 계산하는 내부 함수
    const getSquaredDistance = (p1: Point, p2: Point): number => {
        return Math.pow(p1.lat - p2.lat, 2) + Math.pow(p1.lon - p2.lon, 2);
    };

    const closestPoint = points.reduce((closest, current) => {
        const distToClosest = getSquaredDistance(closest, center);
        const distToCurrent = getSquaredDistance(current, center);

        return distToCurrent < distToClosest ? current : closest;
    });

    return closestPoint;
}

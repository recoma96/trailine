import type { Interval, CourseIntervalResponseSchema } from "@/types/responses/course-interval";
import type { IntervalPoint } from "@/types/common/location";
import React, { useRef, useEffect, useState } from "react";
import { calculateMediumPoint } from "@/lib/calculator";
import { createMarkerHtml } from "@/lib/map-marker";
import { INTERVAL_DIFFICULTY_COLORS } from "@/vars/colors";


interface Props {
    intervalCount: number;
    intervals: Interval[];
    className: string;
};


const CourseMap: React.FC<Props> = ({intervalCount, intervals, className} : Props) => {
    const mapRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const allPointArray: IntervalPoint[] = intervals.flatMap((interval) => interval.points);
        const centerPoint = calculateMediumPoint(allPointArray);

        // 맵 로딩 
        if (mapRef.current) {
            const map = new naver.maps.Map(mapRef.current, {
                center: new naver.maps.LatLng(centerPoint.lat, centerPoint.lon),
                zoom: 15,
            });

            intervals.forEach((interval, idx) => {
                const path = interval.points.map((point) => new naver.maps.LatLng(point.lat, point.lon));
                new naver.maps.Polyline({
                    map: map,
                    path: path,
                    strokeWeight: 4,
                    strokeColor: INTERVAL_DIFFICULTY_COLORS[interval.difficulty.level],
                });
                const firstPoint = path[0];

                const marker = new naver.maps.Marker({
                    position: firstPoint,
                    map: map,
                    icon: {
                        content: createMarkerHtml(idx + 1, interval.difficulty.level),
                        anchor: new naver.maps.Point(15, 15),
                    }
                });
            });
        }
    }, []);


    return (
        <div>
            {mapRef && <div ref={mapRef} className={`${className}`} />}
            {/* mapRef의 초기 데이터가 null임에도 useEffect가 작동되는 이유는, div태그에 ref으로 연결을 했기 때문이다. */}
        </div>
    )
}

export default CourseMap;
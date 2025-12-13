import type { Interval, CourseIntervalResponseSchema } from "@/types/responses/course-interval";
import type { IntervalPoint } from "@/types/common/location";
import React, { useRef, useEffect, useState } from "react";
import { calculateMediumPoint } from "@/lib/calculator";


interface Props {
    intervalCount: number;
    intervals: Interval[];
};


const CourseMap: React.FC<Props> = ({intervalCount, intervals} : Props) => {
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
        }
    }, []);


    return (
        <div>
            {mapRef && <div ref={mapRef} className="w-full h-[600px]" />}
            {/* mapRef의 초기 데이터가 null임에도 useEffect가 작동되는 이유는, div태그에 ref으로 연결을 했기 때문이다. */}
        </div>
    )
}

export default CourseMap;
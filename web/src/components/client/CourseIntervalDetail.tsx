import type { Interval, CourseIntervalResponseSchema } from "@/types/responses/course-interval";
import React, { useEffect, useState } from "react";
import CourseMap from "./CourseMap";


interface Props {
    courseId: number | undefined;
}


const CourseIntervalDetail: React.FC<Props> = ({courseId} : Props) => {
    const [intervalCount, setIntervalCount] = useState<number>(0);
    const [intervals, setIntervals] = useState<Interval[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    if (courseId === null) {
        return (<div>지도를 불러올 수가 없어요.</div>)
    }

    useEffect(() => {
        if (courseId === null) return;

        setLoading(true);

        fetch(`${import.meta.env.PUBLIC_API_ENDPOINT}/v1/courses/${courseId}/intervals`)
            .then((res) => {
                if (!res.ok) {
                    throw new Error('Failed to fetch intervals');
                }
                return res.json();
            })
            .then((data: CourseIntervalResponseSchema) => {
                setIntervals(data.intervals);
                setIntervalCount(data.intervalCount);
            })
            .catch((error) => {
                console.error('Error fetching intervals:', error);
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div><h1>로딩중</h1></div>
    if (intervals.length === 0) return <div><h1>데이터가 없습니다.</h1></div>

    return (
        <div>
            <CourseMap intervalCount={intervalCount} intervals={intervals} />
        </div>
        
    );
}


export default CourseIntervalDetail;

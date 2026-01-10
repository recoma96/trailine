import type { Interval, CourseIntervalResponseSchema } from "@/types/responses/course-interval";
import React, { useEffect, useState } from "react";
import CourseMap from "./CourseMap";
import CheckIcon from "@/components/client/CheckIcon";
import { INTERVAL_DIFFICULTY_COLORS } from "@/vars/colors";
import ImageSlider from "@/components/client/ImageSlider";
import { minutesToKoreanDuration } from "@/lib/string-mapper";


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
        <div className="lg:flex lg:gap-10 w-full">
            <CourseMap intervalCount={intervalCount} intervals={intervals} className="w-full h-[600px] lg:w-full lg:flex-1 lg:min-w-0" />
            <ul className="mt-10 lg:flex-1 lg:min-w-0 flex flex-col gap-y-3">
                {intervals.map((interval, idx) => (
                    <li>
                        <div className="collapse bg-base-100 border-base-300 border">
                            <input type="checkbox" />
                            <div
                                className="collapse-title font-semibold text-white lg:w-auto w-full"
                                style={{background: INTERVAL_DIFFICULTY_COLORS[interval.difficulty.level]}}>{
                                    idx + 1}. {interval.name} [{interval.difficulty.name}] ({interval.length} km, {minutesToKoreanDuration(interval.duration)})
                            </div>
                            <div className="collapse-content text-sm pt-5">
                                {interval.images && interval.images.length > 0 && (
                                    <ImageSlider images={interval.images.map((image) => ({
                                        url: image.url,
                                        title: image.title ?? "",
                                        description: image.description,
                                    }))} className="max-w-full mx-auto mb-4" height={400} />
                                )}
                                <p>{interval.description}</p>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}


export default CourseIntervalDetail;

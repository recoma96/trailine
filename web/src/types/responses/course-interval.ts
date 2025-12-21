import type { IntervalPoint } from "@/types/common/location";

interface IntervalImage {
    title: string | null;
    description: string | null;
    url: string;
};

interface Difficulty {
    id: number;
    name: string;
    code: string;
    level: number;
};

interface Place {
    id: number;
    name: string;
    loadAddress: string | null;
    roadAddress: string | null;
    lat: number;
    lon: number;
    ele: number | null;
};

export interface Interval {
    name: string;
    description: string | null;
    images: IntervalImage[];
    difficulty: Difficulty;
    startPlace: Place;
    endPlace: Place;
    points: IntervalPoint[];
};


export interface CourseIntervalResponseSchema {
    intervalCount: number;
    intervals: Interval[];
};

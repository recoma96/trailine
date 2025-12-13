export interface Point {
    lat: number;
    lon: number;
};

export interface IntervalPoint extends Point {
    ele: number;
};

export interface PlacePoint extends Point {
    ele: number | null;
};
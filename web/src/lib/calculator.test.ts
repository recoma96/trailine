import {describe, it, expect} from 'vitest';
import { calculateMediumPoint } from './calculator';
import type { Point } from '@/types/common/location';

describe('calculateMediumPoint() - 위경도가 들어있는 Point배열을 받고, 그 포인트 중 가장 중앙에 있는 Point를 반환하는 함수', () => {
    it.each([
        {
            name: '배열에서 가장 중앙에 위치한 점을 찾아야 한다.',
            points: [
                { lat: 0, lon: 0 },
                { lat: 0, lon: 10 },
                { lat: 10, lon: 10 },
                { lat: 10, lon: 0 },
                { lat: 4, lon: 4 }, // 이 점이 중앙에 가장 가깝습니다 (평균: 5, 5)
            ],
            expected: { lat: 4, lon: 4 },
        },
        {
            name: '점 배열에 점이 하나만 있는 경우 해당 점을 반환해야 한다.',
            points: [
                { lat: 10, lon: 20 }
            ],
            expected: { lat: 10, lon: 20 },
        },
        {
            name: '모든 점이 같은 위치에 있을 때 해당 점을 반환해야 한다.',
            points: [
                { lat: 5, lon: 5 },
                { lat: 5, lon: 5 },
                { lat: 5, lon: 5 },
            ],
            expected: { lat: 5, lon: 5 }
        },
        {
            name: '음수 죄표에도 올바르게 작동되어야 한다.',
            points: [
                { lat: -10, lon: -10 },
                { lat: 10, lon: 10 },
                { lat: -2, lon: -3 }, // 중심점은 (lat: -0.66, lon: -1) 이므로 이 점이 가장 가깝습니다.
            ],
            expected: { lat: -2, lon: -3 }
        }
    ])('$name', ({points, expected}) => {
        const mediumPoint = calculateMediumPoint(points);
        expect(mediumPoint).toEqual(expected);
    });
});

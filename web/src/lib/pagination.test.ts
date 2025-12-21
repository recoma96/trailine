import {describe, it, expect} from 'vitest';
import { getPaginationItems } from './pagination';


describe('getPaginationItems() - 페이지 개수와 현재 페이지 번호에 따른 페이지네이션 아이템을 반환하는 함수', () => {
    it.each([
        {
            name: '페이지 개수가 4이고, 현재 페이지가 2인 경우',
            currentPage: 2,
            totalPages: 4,
            expected: ['1', '2', '3', '4']
        },
        {
            name: '페이지 개수가 7이고, 현재 페이지가 4인 경우',
            currentPage: 4,
            totalPages: 7,
            expected: ['1', '...', '3', '4', '5', '...', '7']
        },
        {
            name: '페이지 개수가 1이고, 현재 페이지가 1인 경우',
            currentPage: 1,
            totalPages: 1,
            expected: ['1']
        },
        {
            name: '페이지 개수가 2이고, 현재 페이지가 2인 경우',
            currentPage: 2,
            totalPages: 2,
            expected: ['1', '2']
        },
        {
            name: '페이지 개수가 6이고, 현재 페이지가 6인 경우',
            currentPage: 6,
            totalPages: 6,
            expected: ['1', '...', '5', '6']
        },
        {
            name: '페이지 개수가 6이고, 현재 페이지가 1인 경우',
            currentPage: 1,
            totalPages: 6,
            expected: ['1', '2', '...', '6']
        },
        {
            name: '페이지 개수가 10이고, 현재 페이지가 5인 경우',
            currentPage: 5,
            totalPages: 10,
            expected: ['1', '...', '4', '5', '6', '...', '10']
        },
    ])("$name", ({ currentPage, totalPages, expected }) => {
        const result = getPaginationItems(currentPage, totalPages);
        expect(result).toEqual(expected);
    });
});
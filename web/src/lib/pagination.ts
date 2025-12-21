
/**
 * 페이지네이션 아이템을 생성하기 위한 번호 배열을 반환하는 함수 입니다.
 * 
 * 예시:
 *  - 페이지 개수가 4이고, 현재 페이지가 2인 경우: ["1", "2", "3", "4"]
 *  - 페이지 개수가 7이고, 현재 페이지가 4인 경우: ["1", "...", "3", "4", "5", "...", "7"]
 *  - 페이지 개수가 1이고, 현재 페이지가 1인 경우: ["1"]
 *  - 페이지 개수가 2이고, 현재 페이지가 2인 경우: ["1", "2"]
 *  - 페이지 개수가 6이고, 현재 페이지가 6인 경우: ["1", "...", "5", "6"]
 *  - 페이지 개수가 6이고, 편재 페이지가 1인 경우: ["1", "2", "...", "6"]
 * 
 * @param currentPage 현재 페이지 위치 (1번부터 시작)
 * @param totalPages 전체 페이지 개수
 * @returns 페이지네이션 아이템 배열
 */
export function getPaginationItems (currentPage: number, totalPages: number): string[] {

    if (totalPages <= 1) {
        return totalPages === 1 ? ["1"] : [];
    }

    // totalPages가 5 이하일 경우 모든 페이지 번호를 표시합니다.
    if (totalPages <= 5) {
        return Array.from({ length: totalPages }, (_, i) => (i + 1).toString());
    }
    
    const delta = 1;
    const left = currentPage - delta;
    const right = currentPage + delta + 1;
    const range: number[] = [];
    const rangeWithDots: (string|number)[] = [];
    let l: number | undefined;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= left && i < right)) {
            range.push(i);
        }
    }

    for (const i of range) {
        if (l) {
            if (i - l > 1) {
                rangeWithDots.push('...');
            }
        }
        rangeWithDots.push(i);
        l = i;
    }

    return rangeWithDots.map(i => i.toString());
}
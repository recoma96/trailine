
import React, { useState, useEffect } from 'react';

// Type Definitions
type DifficultySchema = {
    id: number;
    code: string;
    name: string;
    level: number;
};

type StyleSchema = {
    id: number;
    code: string;
    name: string;
};

const SearchBar: React.FC = () => {
    // Dropdown data
    const [difficulties, setDifficulties] = useState<DifficultySchema[]>([]);
    const [styles, setStyles] = useState<StyleSchema[]>([]);

    // Filters
    const [selectedDifficulty, setSelectedDifficulty] = useState<string>("0");
    const [selectedStyle, setSelectedStyle] = useState<string>("0");
    
    // Search term
    const [searchWord, setSearchWord] = useState<string>("");

    // Fetch initial data and set state from URL
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        setSearchWord(urlParams.get("word") || "");
        setSelectedDifficulty(urlParams.get("difficulty") || "0");
        setSelectedStyle(urlParams.get("courseStyle") || "0");

        const fetchData = async () => {
            try {
                const [difficultyResponse, styleResponse] = await Promise.all([
                    fetch(`${import.meta.env.PUBLIC_API_ENDPOINT}/v1/courses/difficulties`),
                    fetch(`${import.meta.env.PUBLIC_API_ENDPOINT}/v1/courses/styles`)
                ]);

                if (!difficultyResponse.ok || !styleResponse.ok) {
                    throw new Error('Failed to fetch dropdown data');
                }

                const [difficultiesData, stylesData]: [DifficultySchema[], StyleSchema[]] = await Promise.all([
                    difficultyResponse.json(),
                    styleResponse.json()
                ]);

                setDifficulties(difficultiesData);
                setStyles(stylesData);
            } catch (error) {
                console.error("Failed to initialize component data:", error);
            }
        };

        fetchData();
    }, []);

    const handleSearch = () => {
        const params = new URLSearchParams();
        if (searchWord) params.append('word', searchWord);
        if (selectedDifficulty && selectedDifficulty !== '0') params.append('difficulty', selectedDifficulty);
        if (selectedStyle && selectedStyle !== '0') params.append('courseStyle', selectedStyle);
        params.append('page', '1');

        window.location.href = `/courses?${params.toString()}`;
    };

    const handleDropdownSelect = (type: 'difficulty' | 'style', id: string) => {
        if (type === 'difficulty') {
            setSelectedDifficulty(id);
        } else {
            setSelectedStyle(id);
        }
        // Direct DOM manipulation removed. State update will trigger re-render.
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement) activeElement.blur();
    };

    const handleFilterReset = () => {
        window.location.href = '/courses';
    };

    // Determine button text based on state
    const difficultyButtonText = difficulties.find(d => String(d.id) === selectedDifficulty)?.name || '난이도';
    const styleButtonText = styles.find(s => String(s.id) === selectedStyle)?.name || '코스 스타일';
    const hasActiveFilter = selectedDifficulty !== '0' || selectedStyle !== '0' || searchWord !== '';

    return (
        <div className="w-full max-w-full lg:w-[700px] p-4">
            <div className="card border border-base-content/10 bg-base-100 p-5">
                {/* Filter Section */}
                <div className="flex flex-wrap items-center gap-2">
                    {/* Difficulty Dropdown */}
                    <div className="dropdown" data-filter-type="difficulty">
                        <div tabIndex={0} role="button" className="btn m-1" data-default-text="난이도">
                            {selectedDifficulty === '0' ? '난이도' : difficultyButtonText}
                        </div>
                        <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                            <li><a onClick={() => handleDropdownSelect('difficulty', '0')}>전체</a></li>
                            {difficulties.map(difficulty => (
                                <li key={difficulty.id}>
                                    <a onClick={() => handleDropdownSelect('difficulty', String(difficulty.id))}>
                                        [Lv.{difficulty.level}] {difficulty.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Course Style Dropdown */}
                    <div className="dropdown" data-filter-type="style">
                        <div tabIndex={0} role="button" className="btn m-1" data-default-text="코스 스타일">
                            {selectedStyle === '0' ? '코스 스타일' : styleButtonText}
                        </div>
                        <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                            <li><a onClick={() => handleDropdownSelect('style', '0')}>전체</a></li>
                            {styles.map(style => (
                                <li key={style.id}>
                                    <a onClick={() => handleDropdownSelect('style', String(style.id))}>
                                        {style.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Reset Button */}
                    {hasActiveFilter && (
                        <button className="btn m-1" onClick={handleFilterReset}>
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            초기화
                        </button>
                    )}
                </div>

                {/* Divider */}
                <div className="divider my-2"></div>

                {/* Search Input and Button */}
                <div className="form-control w-full">
                    <div className="input-group flex">
                        <input
                            type="text"
                            placeholder="검색하고 싶은 코스를 입력하세요..."
                            className="input input-bordered w-full"
                            value={searchWord}
                            onChange={(e) => setSearchWord(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        />
                        <button className="btn btn-square" onClick={handleSearch}>
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SearchBar;

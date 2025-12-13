interface Difficulty {
    id: number;
    name: string;
    code: string;
    level: number;
};

interface Style {
    id: number;
    code: string;
    name: string;
};

interface Image {
    title: string;
    description: string | null;
    url: string;
};

export interface CourseDetailSchemaResponse {
    id: number;
    name: string;
    description: string | null;
    loadAddresses: string[];
    roadAddresses: string[];
    difficulty: Difficulty;
    styles: Style;
    images: Image[];
};

export type Tag = 
    | 'Digital tool'
    | 'Book'
    | 'Partnership'
    | 'Historical ecology'
    | 'Environmental governance'
    | 'Ecological democracy'
    | 'Active restoration';

export const tagColors: Record<Tag, string> = {
    'Digital tool': '#E1FFB7',
    'Book': '#FEC3F9',
    'Partnership': '#FFE694',
    'Historical ecology': '#C8B500',
    'Environmental governance': '#B1F6FF',
    'Ecological democracy': '#D5B0FE',
    'Active restoration': '#F67BD6'
};

export interface Project {
    imgurl: string;
    title: string;
    desc: string;
    tags: Tag[];
    imageBackground?: string;
    /** Optional external "Read more" URL */
    link?: string;
}


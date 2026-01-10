import React from 'react';
// Import Swiper React components
import { Swiper, SwiperSlide } from 'swiper/react';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

// import required modules
import { Navigation, Pagination, Mousewheel, Keyboard } from 'swiper/modules';

type Image = {
    title: string;
    description: string | null;
    url: string;
};

interface ImageSliderProps {
    images: Image[];
    className?: string;
    height: number;
}

const ImageSlider: React.FC<ImageSliderProps> = ({ images, className, height }) => {
    if (className === undefined) className = "";
    return (
        <div className={`${className} bg-black`}>
            <Swiper
                loop={true}
                cssMode={true}
                navigation={true}
                pagination={{ clickable: true }}
                mousewheel={true}
                keyboard={true}
                modules={[Navigation, Pagination, Mousewheel, Keyboard]}
                className="mySwiper [--swiper-navigation-color:#fff] [--swiper-pagination-color:#fff]"
            >
                {images.map((image, index) => (
                    <SwiperSlide key={index}>
                        <div className="relative flex">
                            <div className="absolute left-0 top-0 z-10 bg-black bg-opacity-50 p-2 text-sm text-white">
                                {image.title}
                            </div>
                            <img 
                                src={image.url} 
                                alt={image.title} 
                                className="block w-full object-contain"
                                style={{height: `${height}px`}}
                            />
                        </div>
                    </SwiperSlide>
                ))}
            </Swiper>
        </div>
    );
};

export default ImageSlider;

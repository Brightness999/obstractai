import React, { useState, useEffect } from "react";

const Pending = () => {
    
    useEffect(()=>{
        console.log('dfd');
    }, []);
    return (
        <div className="my-6">
			<h1 className="title is-size-2 has-text-centered py-6">Please wait for response of SuperUser!</h1>
        </div>
    )
}

export default Pending;
import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const IndicatorTable = (props) => {
	return (
        <Tr>
            <Td>{`${props.indicator.globalindicator.type}(${props.indicator.globalindicator.type_api})`}</Td>
            <Td>{`${props.indicator.globalindicator.value}(${props.indicator.globalindicator.value_api})`}</Td>
            <Td>
                <div className={props.isAutoDown ? "button is-static" : "button is-text"} onClick={()=>props.IndicatorEnable(props.index)}>
                    <span>{props.indicator.enabled}</span>
                </div>
            </Td>
        </Tr>
	);
}

export default IndicatorTable;
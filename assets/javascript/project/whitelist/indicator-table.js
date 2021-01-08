import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const IndicatorTable = (props) => {
	return (
        <Tr>
            <Td>{`${props.indicator.globalindicator.type}(${props.indicator.globalindicator.type_api})`}</Td>
            <Td>{`${props.indicator.globalindicator.value}(${props.indicator.globalindicator.value_api})`}</Td>
            <Td>
                <a onClick={()=>props.IndicatorEnable(props.index)}>
                    <div className="button is-text">
                        <span>{props.indicator.enabled}</span>
                    </div>
                </a>
            </Td>
        </Tr>
	);
}

export default IndicatorTable;
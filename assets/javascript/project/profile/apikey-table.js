import React from "react";
import { Tr, Td } from 'react-super-responsive-table';


const APIKeyTable = (props) => {

    return (
        <Tr>
            <Td>{props.apikey.value}</Td>
            <Td>{props.apikey.name}</Td>
            <Td>{props.apikey.intelgroup.name}</Td>
            <Td><button className="button is-text" onClick={()=>props.deleteAPIKey(props.index)} >Delete</button></Td>
        </Tr>
    );
}

export default APIKeyTable;
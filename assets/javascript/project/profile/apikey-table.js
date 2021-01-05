import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

import Styles from "../styles";

const APIKeyTable = (props) => {

    return (
        <Tr>
            <Td>{props.apikey.value}</Td>
            <Td>{props.apikey.name}</Td>
            <Td>{props.apikey.intelgroup.name}</Td>
            <Td><button className="button is-text" >Delete</button></Td>
        </Tr>
    );
}

export default APIKeyTable;
import { useContext } from 'react';
import { AuthContext } from './AuthContext';

// custom hook for accessing authentication context
export const useAuth = () => {
    return useContext(AuthContext);
};
